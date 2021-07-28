import resource
import executeAnsibleResources
import executePythonResources
import executeGoResources
import executeTerraformResources
import sys, os, json, shutil


class executeResources(object):

    exe = []
    resource_dict = {
            'FC Networks': 'fc_networks',
            'FCoE Networks': 'fcoe_networks',
            'Ethernet Networks': 'ethernet_networks',
            'Network Sets': 'network_sets',
            'Connection Templates': 'connection_templates',
            'Certificates Server': 'certificates_server',
            'Enclosures': 'enclosures',
            'Enclosure Groups': 'enclosure_groups',
            'Firmware Drivers': 'firmware_drivers',
            'Hypervisor Cluster Profiles': 'hypervisor_cluster_profiles',
            'Hypervisor Managers': 'hypervisor_managers',
            'Interconnects': 'interconnects',
            'Interconnect Types': 'interconnect_types',
            'Logical Enclosures': 'logical_enclosures',
            'Logical Interconnects': 'logical_interconnects',
            'Logical Interconnect Groups': 'logical_interconnect_groups',
            'Scopes': 'scopes',
            'Server Hardware': 'server_hardware',
            'Server Hardware Types': 'server_hardware_types',
            'Server Profiles': 'server_profiles',
            'Server Profile Templates': 'server_profile_templates',
            'Storage Pools': 'storage_pools',
            'Storage Systems': 'storage_systems',
            'Storage Volume Templates': 'storage_volume_templates',
            'Storage Volume Attachments': 'storage_volume_attachments',
            'Volumes': 'volumes',
            'Tasks': 'tasks',
            'Uplink Sets': 'uplink_sets'
        }

    def __init__(self, selected_sdk, api_version):
        #super(executeResources, self).__init__(selected_sdk, api_version)
        self.selected_sdk = selected_sdk
        self.api_version = api_version
#        self.generate_config_values()
        self.success_files = []
        self.failed_files = []

    def generate_config_values(self):
        shutil.copyfile(os.getcwd() + '/oneview-' + self.selected_sdk + '/examples/config-rename.json', os.getcwd() + '/oneview-' + self.selected_sdk + '/examples/config-rename_dummy.json')
        os.rename(os.getcwd() + '/oneview-' + self.selected_sdk + '/examples/config-rename.json', os.getcwd() + '/oneview-' + self.selected_sdk + '/examples/config.json')
        with open(os.getcwd() + '/oneview-' + self.selected_sdk + '/examples/config.json', 'r') as config:
            json_object = json.load(config)
            json_object["ip"] = "10.1.19.63"
            json_object["credentials"]["userName"] = "Administrator"
            json_object["credentials"]["password"] = "admin123"
            json_object["credentials"]["authLoginDomain"] = ""
            json_object["image_streamer_ip"] = ""
            json_object["api_version"] = "3200"
            json_object["server_certificate_ip"] = "172.18.13.11"
            json_object["hypervisor_manager_ip"] = "172.18.13.11"
            json_object["hypervisor_user_name"] = "dcs"
            json_object["hypervisor_password"] = "dcs"
            json_object["storage_system_hostname"] = ""
            json_object["storage_system_username"] = ""
            json_object["storage_system_password"] = ""
            json_object["storage_system_family"] = ""
            with open(os.getcwd() + '/oneview-' + self.selected_sdk + '/examples/config.json', 'w') as config:
                json.dump(json_object, config)
    
   
    def execute(self, resource_dict):
        if self.selected_sdk == 'python':
            python_executor = executePythonResources.executePythonResources(resource_dict)
            executed_files = python_executor.run_python_executor()
        # elif self.selected_sdk == 'ansible':
        #     executed_files = executeAnsibleResources.run_ansible_executor(self)
        # elif self.selected_sdk == 'go' or self.selected_sdk == 'golang':
        #     executed_files = executeGoResources.run_go_executor()
        # elif self.selected_sdk == 'terraform':
        #     executed_files = executeTerraformResources.run_terraform_executor()
        else:
            print("Invalid SDK")
    
        return executed_files
    
