import requests
import json
import logging
import os.path
import time
from copy import deepcopy

rest_call_timeout_sec = 60
max_retries_in_session = 50
polling_call_timeout_sec = 10 * 60
sec_between_polling = 10

class FirstTimeSetUp(object):

    def __init__(self, appliance_name, use_ip=False, override_version=None, retries=max_retries_in_session, appliance_admin_creds=None, appliance_dhcp_ip_address=None
                 post_eula_delay=0, use_static_ip=False, use_one_ip=False, ipv6_type=None, ova_ip=None, host_data=None)):
        """Constructor method to RestAppliance.
        We compute the correct API-Version for REST calls.
            The version can be overridden by passing in a value for override_version.
            Ideally, this computation should be moved to a default in the datastore.

        Parameters
        ----------
        appliance_name : str
            fully qualified name of the appliance
        use_ip : bool
            Flag to indicate if an IP address is being passed instead of DNS hostname.
        override_version (Optional): int
            The default version string (determined by program name) can be overridden.
            Currently only accepting values of 100, 199, and 200.
        retries (Optional): int
            Number of retries to do in HTTP session.
        appliance_admin_creds (Optional): dict
            A dictionary with appliance Administrator login and password if it is different from default.
        appliance_dhcp_ip_address : str
            appliance dhcp ip address, will be used to connect to the appliance if not None
        """
        self.fqdn = appliance_name
        if appliance_dhcp_ip_address:
            self.base_url = "https://" + appliance_dhcp_ip_address
        else:
            self.base_url = "https://" + appliance_name
        self.use_ip = use_ip
        self.appliance_admin_creds = appliance_admin_creds

        # create a persistant session so that we can retry if the appliance goes offline (e.g. first time setup)
        self.sess = requests.Session()
        self.retries = retries
        adap = requests.adapters.HTTPAdapter(max_retries=self.retries)
        self.sess.mount('http://', adap)
        self.sess.mount('https://', adap)

        # if version is passed in, use that.  Else use the default for the program
        # Default to the minimal version number that implements all the requirements that we need. Defined per program.
        # Eventually we may need version overrides at each REST call.
        if not override_version:
            self.api_version = 120
        else:
            self.api_version = override_version

        logging.info("The API Version utilized is {0}.".format(self.api_version))
        self._header = {'X-API-Version': '{}'.format(self.api_version), 'Content-Type': 'application/json'}
        self._secure_header = {}
        
    def get_secure_headers(self):
        """Helper method to appliance_request().
        Gives header information required by the appliance with authentication information.

        Return
        ------
        _secure_header: dict. Dictionary containing X-API-Verions, Content-Type, and Auth.  The Auth parameter value is a sessionID.
        """
        # Once _secure_header is defined, we can use it over and over again for the duration of its life.
        # Note, the header is only good for that user (administrator), 24 hours, and until the next reboot.
        if self._secure_header:
            return self._secure_header   
        payload = {"userName": "Administrator", "password": "admin123"}
        url = '/rest/login-sessions'
        try:
            r = self.sess.post(self.base_url + url, verify=False, headers=self._header, data=json.dumps(payload), timeout=rest_call_timeout_sec)
        except requests.exceptions.RequestException as e:
            raise Exception("There was an issue connecting to the appliance to get headers. Exception message: {0}".format(e))
        except Exception as e:
            raise Exception("There was an issue with the HTTP Call to get headers. Exception message: {0}".format(e))
        if r.status_code >= 300:
            raise Exception('Failure to get secure connection. Status {0}.'.format(r.status_code))
        try:
            safe_json = r.json()
            self._secure_header = self._header.copy()
            self._secure_header['Auth'] = safe_json.get('sessionID')
            if self._secure_header['Auth'] is None:
                raise Exception('Auth token for the header is undefined.  No Session ID available. Status: {0}.'.format(r.status_code))
            return self._secure_header
        except ValueError as e:
            raise Exception('Failure to get a JSON value from the response. Status: {0}.'.format(r.status_code))
        except:
            raise Exception('Failure to access the sessionID from the response. Status: {0}. JSON: {1}'.format(r.status_code, r.json()))

    def appliance_request(self, request_type, url, secure=True, payload=None, other_properties={}, extra_headers={}, poll=True,
                          timeout=None):
        """Helper method to call HTTP requests.
        An exception will be raised if an unknown value for request_type is utilized.
        Exceptions will also be raised if the appliance cannot be contacted.
        If secure=True, this function depends on get_secure_headers().

        Parameters
        ----------
        request_type: str
            accepted values are: "POST", "PUT", "GET", "DELETE"
            Any other value will raise an error.
        url: str
            url location of the REST call. This method concatenates https:// and the fully qualified domain name of the system with this string.
        secure (optional): boolean
            True requests data adding a header that includes authentiation information.
            False requests data without authentication information
            no value defaults in True
        payload (optional): dict
            Python object payload for POST or PUT calls, to be serialized into JSON.
        other_properties (optional): dict
            A dictionary of extra properties that we can give to the Python Request module.
            The dictionary is unpacked and added to Request.
            For example: other_properties={'stream': True}
        poll : boolean
            If false, polling tasks will return immiedtaly - needed for failover setups
        timeout: None or integer
            Defaults to rest_call_timeout_sec if 'None' or unspecified

        Return
        ------
        return (success, r, safe_json_result, polling_results)
        A tuple with these values:
            success: bool. A True/False value.  True indicates that the status_code was under 300 and the polling was successful.
            r: a response object from a Requests call.
            safe_json_results: the JSON returned from the HTTP request. None if the request did not return a JSON value.
            polling_results: dict. dictionary with two values, task_state and task_status.  Both are populated whenever the call requires task polling.
        """
        if timeout is None:
            timeout = rest_call_timeout_sec

        if not secure:
            head = self._header
        else:
            head = self.get_secure_headers()

        head = dict(head.items() + extra_headers.items())

        full_url = self.base_url + url
        logging.debug("Preparing HTTP {0} request.".format(request_type))
        logging.debug("Preparing URL: {0}.".format(full_url))
        logging.debug("Preparing Headers: {0}.".format(head))
        logging.debug("Preparing Payload: {0}.".format(json.dumps(payload)))
        polling_results = {}
        try:
            if request_type == "POST":
                r = self.sess.post(full_url, verify=False, headers=head, data=json.dumps(payload), timeout=timeout, **other_properties)
            elif request_type == "PUT":
                r = self.sess.put(full_url, verify=False, headers=head, data=json.dumps(payload), timeout=timeout, **other_properties)
            elif request_type == "GET":
                r = self.sess.get(full_url, verify=False, headers=head, timeout=timeout, **other_properties)
            elif request_type == "DELETE":
                r = self.sess.delete(full_url, verify=False, headers=head, timeout=timeout, **other_properties)
            else:
                raise Exception("RestAppliance attempted to call an http request other than POST, PUT, or GET. request_type: {0}. url: {1}".format(request_type, url))
            try:
                safe_json_result = r.json()
            except:
                safe_json_result = {}
            logging.debug("Returned. Status code: {0}.".format(r.status_code))
            logging.debug("Returned. JSON: {0}.".format(safe_json_result))
            # 202 status codes indicate a task that is pollable. The calling function may not know that this will return a 202.
            success = False
            if r.status_code == 202:
                if not poll:
                    return (True, r, safe_json_result, {'task_state': 'N/A', 'task_status': 'N/A'})
                (task_state, task_status) = self.poll_for_task(url, r)
                polling_results = {'task_state': task_state,
                                   'task_status': task_status}
                if task_state == "Completed":
                    success = True
                elif self.use_ip and task_state == "Warning":
                    #This is required sicne FTS will try to validate the hostname and if it is not valid hostname then it will
                    #the warning for post-validation status.
                    success = True

            elif r.status_code < 300:
                success = True
            else:
                polling_results = {'task_state': safe_json_result.get('errorCode', 'Error'),
                                   'task_status': safe_json_result.get('details', str(safe_json_result))}
            return (success, r, safe_json_result, polling_results)
        except requests.exceptions.RequestException as e:
            raise Exception("There was an issue connecting to the appliance. Exception message: {0}".format(e))
        except Exception as e:
            raise Exception("There was an issue with the HTTP Call. Exception message: {0}".format(e))

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
        (_, _, json_result, _) = self.appliance_request(request_type='GET', url=url, secure=False)
        if not json_result:  # if False, eula acceptance has already occurred.
            logging.warning('EULA does not need to be saved.')
        else:
            logging.debug('Call EULA Acceptance with enable service access={0}'.format(service_access))
            url = '/rest/appliance/eula/save'
            payload = {"supportAccess": service_access}
            (save_success, save_resp, save_json_response, _) = self.appliance_request(request_type='POST', url=url, secure=False, payload=payload)
            if save_success:
                logging.info('EULA Accepted.')
            else:
                raise Exception('accept_eula failed. Status: {0}. JSON Response: {1}'.format(save_resp.status_code, json.dumps(save_json_response, sort_keys=True, indent=4, separators=(',', ': '))))

    def accept_eula(self, service_access="yes", tries=3, retry_interval=5):

        thistry = 1
        while True:
            logging.info("accept_eula try {}".format(thistry))
            try:
                self.accept_eula_once(service_access=service_access)
                return
            except Exception as e:
                logging.exception(e)
                if thistry >= tries:
                       raise e
            time.sleep(retry_interval)
            thistry += 1
            
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
        url = '/rest/users/changePassword'

        payload = {"userName": initial_admin,
                   "oldPassword": initial_admin_password,
                   "newPassword": new_admin_password}
        (success, resp, json_response, _) = self.appliance_request(request_type='POST', url=url, secure=False, payload=payload)
        if success:
            logging.info('Administrator password change was accepted.')
        elif resp.status_code == 400:
            logon_url = '/rest/login-sessions'
            logon_payload = {"userName": admin_user, "password": new_admin_password}
            (logon_success, _, _, _) = self.appliance_request(request_type='POST', url=logon_url, secure=False, payload=logon_payload)
            if not logon_success:
                raise Exception('change_administrator_password failed. Status: {0}. JSON Response: {1}'.format(resp.status_code, json.dumps(json_response, sort_keys=True, indent=4, separators=(',', ': '))))
            logging.warning('Administrator password has already been changed. Password is {0}'.format(new_admin_password))
        else:
            raise Exception('change_administrator_password failed. Status: {0}. JSON Response: {1}'.format(resp.status_code, json.dumps(json_response, sort_keys=True, indent=4, separators=(',', ': '))))
            
    def get_mac(self):
        """Request the MAC address from the appliance. Use the first one found in applianceNetworks collection.
        If the appliance returns an error status (anything outside of the 100 or 200 range), an error is raised.

        Parameters
        ----------
        none

        Return
        ------
        mac address: string
        """
        json_answer = self.get_networking_data()
        for network in json_answer.get('applianceNetworks', []):
            mac_address = network.get('macAddress')
            if mac_address:
                logging.info('MAC Address is: {0}'.format(mac_address))
                return mac_address
        raise Exception('MAC Address is not defined')
        
    def get_ipv4_name_servers(self):
        """Request the list of dns ipv4 name servers. Use the first one found in applianceNetworks collection.
        If the appliance returns an error status (anything outside of the 100 or 200 range), an error is raised.

        Parameters
        ----------
        none

        Return
        ------
        list of ipv4 name servers: list
        """
        json_answer = self.get_networking_data()
        for network in json_answer.get('applianceNetworks', []):
            ipv4_name_servers = network.get('ipv4NameServers')
            if ipv4_name_servers:
                logging.info('IPv4 Name servers: {0}'.format(ipv4_name_servers))
                return ipv4_name_servers
        raise Exception('IPv4 Name server is not defined')
            
    def get_networking_data(self):
        """Request the networking information from the appliance.
        If the appliance returns an error status (anything outside of the 100 or 200 range), an error is raised.

        Parameters
        ----------
        none

        Return
        ------
            a response object from a call to the network page.
        """
        url = '/rest/appliance/network-interfaces'
        (success, resp, json_response, _) = self.appliance_request(request_type='GET', url=url, secure=True)
        if not success:
            raise Exception('get_networking_data call failed. Status: {0}. JSON Response: {1}'.format(resp.status_code, json.dumps(json_response, sort_keys=True, indent=4, separators=(',', ': '))))
        return json_response    

    def get_time_locale_data(self):
        """Request the networking information from the appliance.
        If the appliance returns an error status (anything outside of the 100 or 200 range), an error is raised.

        Parameters
        ----------
        none

        Return
        ------
            a response object from a call to the network page.
        """
        url = "/rest/appliance/configuration/time-locale"
        (success, resp, json_response, _) = self.appliance_request(request_type='GET', url=url, secure=True)
        if not success:
            raise Exception('get_time_locale_data call failed. Status: {0}. JSON Response: {1}'.format(resp.status_code, json.dumps(json_response, sort_keys=True, indent=4, separators=(',', ': '))))
        return json_response        

    def set_time_server_and_locale(self, ntpserver):
        """
        If the time definition is not part of the network-interfaces JSON, it is set via an independent REST endpoint.
        :param ntpserver: IP address of the ntpserver.
        :return:
        :raises: Exception, Exception
        """
        time_locale_url = "/rest/appliance/configuration/time-locale"
        # Query for current time-locale setting.
        time_locale_settings = self.get_time_locale_data()  # Exception will be raised by method if it fails.

        time_locale_settings["dateTime"] = None  # our time is not necessarily the NTP time, so don't set it.
        time_locale_settings["ntpServers"] = [str(ntpserver)]  # use the defined NTP server and only it.
        (ntp_success, _, ntp_rjson, ntp_polling_results) = self.appliance_request(request_type='POST',
                                                                                  url=time_locale_url,
                                                                                  secure=True,
                                                                                  payload=time_locale_settings)
        if not ntp_success:
            logging.error(json.dumps(ntp_rjson, sort_keys=True, indent=4, separators=(',', ': ')))
            if 'Wait until the operation completes' in ntp_polling_results.get("task_status"):
                raise Exception(
                    'time-locale setting failed. Polling State: {0}. Polling Status: {1}. '.format(
                        ntp_polling_results.get("task_state"), ntp_polling_results.get("task_status")))
            else:
                raise Exception(
                    'time-locale setting failure. Polling State: {0}. Polling Status: {1}. '.format(
                        ntp_polling_results.get("task_state"), ntp_polling_results.get("task_status")))
        logging.info("NTP server setting was successful")

    def poll_for_task(self, calling_url, response):
        '''Helper method to appliance_request().
        Status Response 202 indicates an asynchronous REST call.  Poll until the task is complete or error.
        Adds to the set of parameters that appliance_request() returns.

        Parameters
        ----------
        calling_url : string
            The URL that was called in appliance_request.
        response : a response object from a Requests call.

        Return
        ------
        tuple containing:
            task_state: str.  A short summary of the execution/completion status
            task_status: str. State of the task.  For Example: Unknown, Running, Terminated, Error, Warning, Completed.
        '''
        # network-interfaces is a special case.  Rather than network-interfaces returning a object of type TaskResourceV2, this end point returns Void.
        # From my reading of the documentation, this is not consistant with the Task Tracker mechanism.  I have brought this to the attention
        #   of the atlas team.
        #
        # there are now at least two responses with the task URL in the header:
        # '/rest/appliance/network-interfaces' and '/rest/appliance/configuration/time-locale'
        # Go to checking for response in the header, if not there, check in the JSON.  Poor consistency in
        # implementations and inconsistent with REST principles.
        url = response.headers.get('location')
        if url is None:
            url = response.json().get('uri')
        if url is None:
            raise Exception('Could not read the task to poll. Originating request on URL: {0}.'.format(calling_url))
        full_rest_url = self.base_url + url
        task_state = 'Running'
        start_time = time.time()
        try:
            logging.debug("Starting polling the rest task {0}.".format(url))
            already_reset_session = False
            while task_state in ['Running', 'New', 'Pending', 'Starting']:
                if time.time() >= start_time + polling_call_timeout_sec:
                    raise Exception('Task Polling did not respond within {0} seconds. Time out and exit. Originating request on URL: {1}'.format(polling_call_timeout_sec, calling_url))
                time.sleep(sec_between_polling)
                r_tree = None
                try:
                    logging.debug("Current Time {0}".format(time.asctime(time.localtime(time.time()))))
                    r_tree = self.sess.get(full_rest_url + "?view=tree", verify=False, headers=self.get_secure_headers(), timeout=rest_call_timeout_sec)
                except Exception as e:
                    logging.exception("FTS get failed: " + str(e))
                    if already_reset_session:
                        raise Exception("There was an issue with the HTTP Call for task polling. Exception message: {0}".format(e))
                    # delete and recreate of the session if it loses connection.  Changes in IP address, FQDN, etc can make use lose the session.
                    else:
                        already_reset_session = True
                        self.sess.close()
                        self.sess = requests.Session()
                        adap = requests.adapters.HTTPAdapter(max_retries=self.retries)
                        self.sess.mount('http://', adap)
                        self.sess.mount('https://', adap)
                if r_tree:
                    r_treejson = r_tree.json()
                    task_resource = r_treejson.get('resource')
                    task_state = task_resource.get('taskState')
                    task_status = task_resource.get('taskStatus', '')
                    task_errors = task_resource.get('taskErrors', None)
                    if task_errors:
                        # in case of errors place them in log output and append to status message
                        for e in task_errors:
                            logging.error(e)
                        task_status += ";" + ";".join([str(e) for e in task_errors])
                    logging.debug("Percent Complete : {0}. State: {1}. Status: {2}.".format(task_resource.get('percentComplete'), task_state, task_status))
                    logging.debug("The task tree for {0} is:".format(full_rest_url))
                    logging.debug("Returned JSON: {0}".format(r_treejson))
                else:
                    logging.debug("Exception during get call, response was not set")
                    logging.debug("Unable to get the task tree for {0}".format(full_rest_url))
            return(task_state, task_status)
        except ValueError as e:
            raise Exception('Error getting the JSON results from the task. Originating request on URL: {0}. Exception: {1}'.format(calling_url, e))
        except Exception as e:
            raise Exception('Error in polling for the task. Originating request on URL: {0}. Exception: {1}'.format(calling_url, e))        
            
    def first_time_setup(self, ntpserver, use_static_ip=False, use_tbird_fts=False, use_i3s_fts=False, use_one_ip=False, ipv6_type=None, ova_ip=None, host_data=None):
        """Creates networking for the appliance.
        Configures the appliance as DHCP.
        The appliance queries itself to define its macAddress.

        If the api_version is above version 100, this will set a DNS Server IP address and set
        the overrideIpv4DhcpDnsServers value to False.
             "ipv4NameServers": [dns_server_ip],
             "overrideIpv4DhcpDnsServers": False
        If the api_version is below version 100, it does not set DNS.

        If the appliance returns an error status (anything outside of the 100 or 200 range), an error is raised.
        """

        url = '/rest/appliance/network-interfaces'
        if ova_ip:
            networking_data = self.get_networking_data()
            network = networking_data['applianceNetworks'][0]
            network["hostname"] = self.fqdn
            network["domainName"] = self.fqdn.split(".", 1)[1]
            network['ipv4Type'] = "STATIC"
            network["searchDomains"] = None
            # this is what UI does so we follow
            network["aliasDisabled"] = True
            network["overrideIpv4DhcpDnsServers"] = False

            if network["app1Ipv4Addr"] == network["virtIpv4Addr"]:
                network["virtIpv4Addr"] = ''
                network["app1Ipv4Addr"] = ova_ip
                network["app2Ipv4Addr"] = ''
            else:
                raise Exception("Impossible happened: app1Ipv4Addr != virtIpv4Addr")
            network["ipv6Type"] = "UNCONFIGURE"
            payload = networking_data

        elif use_static_ip:
            networking_data = self.get_networking_data()
            networks = []
            for network in networking_data['applianceNetworks']:
                if network["ipv4Type"] == "DHCP":
                    network['ipv4Type'] = "STATIC"
                    network['ipv6Type'] = "UNCONFIGURE"
                    networks.append(network)
                if use_i3s_fts:
                    network['ipv6Type'] = "UNCONFIGURE"
                    network["overrideIpv4DhcpDnsServers"] = False
                    network['virtIpv4Addr'] = None
                    networks.append(network)
                    appliance_domain_name = self.fqdn.split(".", 1)[1]
                    if appliance_domain_name not in network["hostname"]:
                        network["hostname"] = network["hostname"] + '.' + appliance_domain_name
                        logging.info("Setting fqdn for the appliance:{0}".format(network["hostname"]))

            networking_data['applianceNetworks'] = networks
            networking_data.pop('serverCertificate', None)
            payload = networking_data
        else:
            appliance_mac_address = self.get_mac()
            ipv4_name_servers = self.get_ipv4_name_servers()
            # Only ipv6 with DHCP is supported, will add static at some point later.
            if ipv6_type != "DHCP":
                ipv6_type = "UNCONFIGURE"
            payload = {"type": "ApplianceServerConfiguration",
                       "applianceNetworks": [{"ipv4Type": "DHCP",
                                              "ipv6Type": ipv6_type,
                                              "macAddress": appliance_mac_address,
                                              "hostname": self.fqdn,
                                              "device": "eth0",
                                              "ipv4NameServers": ipv4_name_servers,
                                              "overrideIpv4DhcpDnsServers": False,
                                              "ipv4Subnet": "",
                                              "ipv4Gateway": None,
                                              "confOneNode": True,
                                              "activeNode": 1
                                              }
                                             ],
                       }
            # Not clear why this conditions fails to query the network interface to get the base for the payload, but
            # we need to know if the network definition has the "time" dictionary defined in it; if it does, copy into
            # place for the test below this set of conditional branches.  Since both get_mac and get_ipv4_name_servers
            # use calls to get_networking_data, this seems poorly designed, but given how complex the code is in this
            # area and the lack of documented test cases, this seems to be the safest change to make.
            old_network = self.get_networking_data()
            if "time" in old_network:
                payload["time"] = deepcopy(old_network["time"])

        # This is the later data model, where the time server and locale are set via their own API
        # This will embed another REST process using POST inside the generation of a POST to do the network setup.
        self.set_time_server_and_locale(ntpserver)

        poll = True
        # Do not poll for the task if a ova_ip is passed in. If a ova_ip is passed in then we will lose connection
        # to the orginal location after the POST command to set the networking. Instead, we will change to the new
        # address and then poll for the task.
        if ova_ip:
            poll = False

        (success, response, rjson, polling_results) = self.appliance_request(request_type='POST', url=url, secure=True, payload=payload, poll=poll)

        # Reset the base url to the the fqdn for any subsequent rest actions and then use the fqdn to make sure the
        # networking setup task completes successfully. This needs to be done for OVA's that are deployed as DHCP but,
        # need to be configured as static since the ip address will change after setting up the networking.
        if ova_ip and success:
            self.base_url = "https://" + self.fqdn
            (task_state, task_status) = self.poll_for_task(url, response)
            polling_results = {'task_state': task_state,
                               'task_status': task_status}
            if task_state == "Completed":
                success = True
            else:
                success = False

        if not success:
            logging.error(json.dumps(rjson, sort_keys=True, indent=4, separators=(',', ': ')))
            if 'Wait until the operation completes' in polling_results.get("task_status"):
                raise Exception('first_time_setup failure. Polling State: {0}. Polling Status: {1}. '.format(polling_results.get("task_state"), polling_results.get("task_status")))
            else:
                raise Exception('first_time_setup failure. Polling State: {0}. Polling Status: {1}. '.format(polling_results.get("task_state"), polling_results.get("task_status")))
        logging.info("First time setup was successful")
        logging.debug(json.dumps(self.get_networking_data(), indent=2, sort_keys=True))
        
        
if __name__ == '__main__':
    ra = FirstTimeSetUp(appliance_name, override_version=version, use_ip=False,
                       appliance_admin_creds=None, appliance_dhcp_ip_address=None,
                       post_eula_delay=0, use_static_ip=False,use_one_ip=False,
                       ipv6_type=None, ova_ip=None, host_data=None)
    ra.accept_eula("yes")
    logging.info("Sleeping {0} seconds to wait for appliance to stabilize".format(post_eula_delay))
    time.sleep(post_eula_delay)
    ra.change_administrator_password()
    ra.first_time_setup(ntpserver, use_static_ip=use_static_ip,
            use_i3s_fts=use_i3s_fts, use_one_ip=use_one_ip, ipv6_type=ipv6_type,
            ova_ip=ova_ip, host_data=host_data)