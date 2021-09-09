from re import search, IGNORECASE
import json, time
from SSHLibrary import SSHLibrary

class dcs(object):

    def __init__(self):
        self.sshlib = SSHLibrary()
        self.stdout = None

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
		
        self.stdout = self.sshlib.execute_command(dcs_command, return_stdout=True)
        if search(expected_output, self.stdout, IGNORECASE) is None:
            raise AssertionError("DCS command output is not as expected: {} found: {}".format(expected_output, self.stdout))
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
        Performs Hardware Setup in DCS appliance and verify
        Example
            DCS Hardware Setup | <timeout> |
        :param timeout: time required for the hardware setup to complete
        '''	
        resp = self.fusion_lib.fusion_api_get_appliance_version()
        apiversions, exit_code = self.sshlib.execute_command(command="curl --request GET https://localhost/rest/version", return_rc=True)
        if exit_code == 0:
            apiVersion = json.loads(apiversions)
            status, exit_code = self.sshlib.execute_command(command="curl -s -o /dev/nul -I -w '%{http_code}\n' -X POST -H X-API-Version:" + apiVersion["currentVersion"] + " https://localhost/rest/appliance/tech-setup", return_rc=True)
            if exit_code != 0 or int(status) != 202:
                raise AssertionError("Failed to Invoke Sever Hardware discovery with status:{} and exit code:{}".format(status, exit_code))

    def dcs_schematic_configuration(self, vm, user, userpwd, dcs_commands):
        '''
        Change DCS schematic then perform Hardware setup
        Example
            Change DCS Schematic | <vm> | <user> | <userpwd> | <dcs_commands> |
        :param vm: DCS vm ip
        :param user: Username for login
        :param userpwd: Password For login
        :param dcs_commands: Sequence of DCS commands to be executed along with its expected output for changing the schematic
                             ex:[["dcs stop", "DCS is Stopped"]]
        '''
        self.sshlib.open_connection(vm)
        self.sshlib.login(username=user, password=userpwd)
        self.change_dcs_schematic(dcs_commands)
        self.dcs_hardware_setup()
        self.sshlib.close_connection()
		
dcs_commands=[
	["dcs status", "dcs is running"],
	["dcs stop", "dcs is stopped"],
	["dcs status", "dcs is not running"],
	["dcs start /dcs/schematic/synergy_3encl_demo cold", "DCS httpd daemon started"],
	["dcs status", "DCS is Running\n  Schematic used:  /dcs/schematic/synergy_3encl_demo"]
]

if __name__ == '__main__':
	dcs_inst = dcs()
	dcs_inst.dcs_schematic_configuration("fe80::e62:ea28:16e9:fe9%ens160", "root", "hponeview", dcs_commands)
