from sdkAutomator.executeAnsibleResources import executeAnsibleResources
import executePythonResources
import executeAnsibleResources


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
        self.success_files = []
        self.failed_files = []

    def execute(self, resource_dict):
        if self.selected_sdk == 'python':
            python_executor = executePythonResources.executePythonResources(resource_dict)
            executed_files = python_executor.run_python_executor()
        elif self.selected_sdk == 'ansible':
            ansible_executor = executeAnsibleResources.executeAnsibleResources()
            executed_files = ansible_executor.run_ansible_executor()
        # elif self.selected_sdk == 'go' or self.selected_sdk == 'golang':
        #     executed_files = executeGoResources.run_go_executor()
        # elif self.selected_sdk == 'terraform':
        #     executed_files = executeTerraformResources.run_terraform_executor()
        else:
            print("Invalid SDK")
    
        return executed_files
    
