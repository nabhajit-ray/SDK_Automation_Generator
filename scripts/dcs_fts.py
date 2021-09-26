from re import search, IGNORECASE
import json, time
from SSHLibrary import SSHLibrary

import requests
import json
import logging
import time
from copy import deepcopy
import platform  # For getting the operating system name
import subprocess  # For executing a shell command


class dcs(object):
    def __init__(self, ipv6="", vmInterface="", user="", userpwd=""):

        # builds endpoint
        self.ipv6Endpoint = ipv6 + "%" + vmInterface

        self.sshlib = SSHLibrary()
        self.stdout = None
        self.sshlib.open_connection(self.ipv6Endpoint)
        self.sshlib.login(username=user, password=userpwd)

        # sets API version
        self.api_version = self.get_api_version()
        logging.info("The API Version utilized is {0}.".format(
            self.api_version))

        # header information
        self._header = "-H \"X-API-Version: {0}\" -H \"Content-Type: application/json\"".format(
            self.api_version)
        self._secure_header = None

    def get_api_version(self):
        # this method gets API verisons from the appliance.
        api_command = "curl --request GET https://localhost/rest/version"
        apiversions, exit_code = self.sshlib.execute_command(
            command=api_command, return_rc=True)
        if exit_code == 0:
            api_version = json.loads(apiversions)
            return api_version["currentVersion"]

        # if exit_code returns error it automatically returns to 120
        else:
            logging.warning(
                "The API Version utilized is 120 as get_api_version return exit code 1"
            )
            return "120"

    def build_command(self, url, request_type, payload={}, *options):
        url = "https://localhost" + url

        if request_type == "GET":
            command = "curl -X {0} {1} {2}".format(request_type, self._header,
                                                   url)
            if self._secure_header != None:
                command = "curl -X {0} {1} {2}".format(request_type,
                                                       self._secure_header,
                                                       url)
        elif request_type == "POST":
            payload = '{0}'.format(json.dumps(payload).replace("'", '"'))
            command = 'curl -X {0} {1} -d \'{2}\' {3}'.format(
                request_type, self._header, payload, url)
            if self._secure_header != None:
                command = 'curl -X {0} {1} -d \'{2}\' {3}'.format(
                    request_type, self._secure_header, payload, url)
        if options:
            option = ""
            for op in options:
                option = option + " " + op
                command = "curl{0} -X {1} {2} -d '{3}' {4}".format(
                    option, request_type, self._header, payload, url)
            if self._secure_header != None:
                command = "curl{0} -X {1} {2} -d '{3}' {4}".format(
                    option, request_type, self._secure_header, payload, url)
            return command
        return command

    def accept_eula_once(self, service_access="yes"):
        """On initial communication with the appliance, the end user service agreement (EULA) must be accepted.
        This only needs to occur once.  Additional calls will not change the status of the EULA nor the status of the service access.
        If a change to the service access is required, see the function change_service_access()
        If the appliance returns an error status (anything outside of the 100 or 200 range), an error is raised.
        No authentication on the appliance is required.
        Parameters
        ----------
        service_access (optional): str
            "yes" will accept service access
            "no" will not allow service access
             empty value will default to "yes"
        """

        url = '/rest/appliance/eula/status'
        eula_command = self.build_command(url, "GET")

        json_result, exit_code = self.sshlib.execute_command(eula_command,
                                                             return_rc=True)
        logging.warning(exit_code)
        if not json_result:  # if False, eula acceptance has already occurred.
            logging.warning('EULA does not need to be saved.')
        if exit_code != 0 or json_result:
            logging.debug(
                'Call EULA Acceptance with enable service access={0}'.format(
                    service_access))
            url = '/rest/appliance/eula/save'
            payload = {"supportAccess": service_access}
            save_eula_command = self.build_command(url, "POST", payload)
            logging.warning(save_eula_command)
            save_success, exit_code = self.sshlib.execute_command(
                save_eula_command, return_rc=True)
            if exit_code == 0:
                logging.info('EULA Accepted.')
            else:
                raise Exception('accept_eula failed. JSON Response {0}'.format(
                    json.dumps(save_success)))

    def change_administrator_password(self):
        """On initial logon, the administrator's password has to be changed from the default value.
        The call to the administrator password change is attempted.
        If the change administrator password call fails, then we attempt to login with the administrator password.
        If successful, we log a message and the accurate administrator password.
        If the administrator login is not successful, an error is raised.
        The administrator data is pulled from the dictionary in this file.  This needs to be moved to a more formal location.
        Parameters
        ----------
        none
        """
        # The changePassword REST end point only works for the initial administrator password change.
        url = "/rest/users/changePassword"
        payload = {
            "userName": "Administrator",
            "oldPassword": "admin",
            "newPassword": "admin123"
        }
        change_pass_command = self.build_command(url, "POST", payload)
        status, success = self.sshlib.execute_command(
            command=change_pass_command, return_rc=True)

        if success == 0:
            logging.info('Administrator password change was accepted.')
        else:
            raise Exception(
                'change_administrator_password failed. JSON Response: {0}'.
                format(json.dumps(status)))

    def get_secure_headers(self):
        """Helper method to appliance_request().
        Gives header information required by the appliance with authentication information.
        Return
        ------
        _secure_header: dict. Dictionary containing X-API-Verions, Content-Type, and Auth.  The Auth parameter value is a sessionID.
        """
        # Once _secure_header is defined, we can use it over and over again for the duration of its life.
        # Note, the header is only good for that user (administrator), 24 hours, and until the next reboot.

        if self._secure_header != None:
            return self._secure_header
        payload = {"userName": "Administrator", "password": "admin123"}
        url = '/rest/login-sessions'

        authentication_command = self.build_command(url, "POST", payload)
        status, exit_code = self.sshlib.execute_command(
            command=authentication_command, return_rc=True)
        if exit_code != 0:
            raise Exception(
                "There was an issue with the HTTP Call to get headers. Exception message: {0}"
                .format(status))
        try:
            safe_json = json.loads(status)
            self._secure_header = self._header
            if 'sessionID' not in safe_json:
                raise Exception(
                    'Auth token for the header is undefined.  No Session ID available. Status: {0}.'
                    .format(status))
            self._secure_header = self._header + ' -H "Auth: {0}"'.format(
                safe_json['sessionID'])
            return self._secure_header
        except:
            raise Exception(
                'Failure to access the sessionID from the response. JSON: {0}'.
                format(status))

    def get_mac(self):
        url = "/rest/appliance/network-interfaces"
        self.get_secure_headers()
        mac_command = self.build_command(url, "GET")
        data, exit_code = self.sshlib.execute_command(command=mac_command,
                                                      return_rc=True)
        if exit_code != 0:
            raise Exception(
                'Failure to get mac address of the interface: {0}'.format(
                    data))
        data = json.loads(data)
        print(data)
        try:
            return data["applianceNetworks"][0]["macAddress"]
        except:
            raise Exception('Failure to fetch macAddress from the reponse')

    def change_ovDcs_ip(
        self,
        app1Ipv4Addr,
        app2Ipv4Addr,
        virtIpv4Addr,
        ipv4Gateway,
        ipv4Subnet,
    ):
        url = "/rest/appliance/network-interfaces"
        macAddress = self.get_mac()
        payload = {
            "applianceNetworks": [{
                "activeNode": 1,
                "app2Ipv4Addr": app2Ipv4Addr,
                "app1Ipv4Addr": app1Ipv4Addr,
                "confOneNode": True,
                "hostname": "ThisIsAutomated.com",
                "networkLabel": "Managed devices network",
                "interfaceName": "Appliance",
                "device": "eth0",
                "ipv4Gateway": ipv4Gateway,
                "ipv4Subnet": ipv4Subnet,
                "ipv4Type": "STATIC",
                "ipv6Type": "UNCONFIGURE",
                "macAddress": macAddress,
                "overrideIpv4DhcpDnsServers": False,
                "unconfigure": False,
                "slaacEnabled": "yes",
                "virtIpv4Addr": virtIpv4Addr
            }]
        }

        changeIp_command = self.build_command(url, "POST", payload, "-i")
        data, exit_code = self.sshlib.execute_command(command=changeIp_command,
                                                      return_rc=True)
        uri = re.search('Locations: (.+?)\r\nCache-Control', str)
        if uri != None:
            task_uri = uri.group(1)
            if (self.get_task(task_uri)):
                logging.Info("Oneview Ip is set to: {0}".format(virtIpv4Addr))
        return None 

    def get_task(self, uri):
        self.get_secure_headers()
        task_command = self.build_command(uri, "GET")
        data, exit_code = self.sshlib.execute_command(command=task_command,
                                                      return_rc=True)
        if exit_code == 0:
            task_data = json.loads(data)
            while task_data["taskState"] == "Running"
                time.sleep(60)
                data = self.get_task(task_uri)
                task_data = json.loads(data)
            if task_data["taskState"] == "Completed":
                return True
            else:
                raise Exception("Failure in changing IP. Task ended with state{0}, URI:{1}".format(task_data["taskState"], uri))
        return None

    def execute_command_in_dcs_and_verify(self, dcs_command, expected_output):
        '''
        Execute the given Command in DCS and verify the response with Expected output.
        Example
            Execute Command In DCS And Verify | <dcs_command> | <expected_output> |
        :param dcs_command: Command that need to be executed in DCS vm
        :param expected_output: expected output from the DCS command executed
        :raises  AssertionError if output does not match with expected output
        :return stdout: return response obtained after command execution
        '''
        self.stdout = self.sshlib.execute_command(dcs_command,
                                                  return_stdout=True)
        if search(expected_output, self.stdout, IGNORECASE) is None:
            raise AssertionError(
                "DCS command output is not as expected: {} found: {}".format(
                    expected_output, self.stdout))
        return self.stdout

    def change_dcs_schematic(self, dcs_commands):
        '''
        Changes DCS schematic to given schematic
        Example
            Change DCS Schematic | <dcs_commands> |
        :param dcs_commands: DCS commands to be executed along with its expected output for changing the schematic
                             ex:[["dcs stop", "DCS is Stopped"]]
        '''
        for cmd in dcs_commands:
            self.execute_command_in_dcs_and_verify(cmd[0], cmd[1])
            time.sleep(60)

    def dcs_hardware_setup(self):
        '''
        Performs Hardware Setup in DCS appliance
        '''
        resp = self.fusion_lib.fusion_api_get_appliance_version()
        apiversions, exit_code = self.sshlib.execute_command(
            command="curl --request GET https://localhost/rest/version",
            return_rc=True)
        if exit_code == 0:
            apiVersion = json.loads(apiversions)
            status, exit_code = self.sshlib.execute_command(
                command=
                "curl -s -o /dev/nul -I -w '%{http_code}\n' -X POST -H X-API-Version:"
                + apiVersion["currentVersion"] +
                " https://localhost/rest/appliance/tech-setup",
                return_rc=True)
            if exit_code != 0 or int(status) != 202:
                raise AssertionError(
                    "Failed to Invoke Sever Hardware discovery with status:{} and exit code:{}"
                    .format(status, exit_code))

    def dcs_schematic_configuration(self, dcs_commands):
        '''
        Change DCS schematic then perform Hardware setup
        :param dcs_commands: Sequence of DCS commands to be executed along with its expected output for changing the schematic
                             ex:[["dcs stop", "DCS is Stopped"]]
        '''
        self.change_dcs_schematic(dcs_commands)
        self.dcs_hardware_setup()
        self.sshlib.close_connection()


dcs_commands = [
    ["dcs status", "dcs is running"], ["dcs stop", "dcs is stopped"],
    ["dcs status", "dcs is not running"],
    [
        "dcs start /dcs/schematic/synergy_3encl_demo cold",
        "DCS httpd daemon started"
    ],
    [
        "dcs status",
        "DCS is Running\n  Schematic used:  /dcs/schematic/synergy_3encl_demo"
    ]
]
if __name__ == '__main__':
	dcs_inst = dcs()
        dcs_inst.dcs_network_configuration()
	dcs_inst.dcs_schematic_configuration("fe80::e62:ea28:16e9:fe9%ens160", "root", "hponeview", dcs_commands)
