
import fnmatch
import executePythonResources
import writeEndPointsFile
import executeResources
import changeLogGenerator
import sys
import os
from datetime import datetime
import subprocess
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
class LogWriter(object):
    """
    To show logs on console and flushing the same to logs file.
    """
    def __init__(self, filename):
        self.stdout = sys.stdout
        self.file = filename

    def write(self, obj):
        self.file.write(obj)
        self.stdout.write(obj)
        self.file.flush()

    def flush(self):
        self.stdout.flush()
        self.file.flush()

def clean_up_files():
    print("---------Removing all log files---------------")
    for rootDir, subdirs, filenames in os.walk(os.getcwd()):
        for filename in fnmatch.filter(filenames, 'logfile*.log'):
            try:
                os.remove(os.path.join(rootDir, filename))
            except OSError:
                print("Error while deleting file")
                print("---------Completed removing log files--------------")
    try:
        folder_names = ['oneview-python', 'oneview-ansible-collections','oneview-golang','oneview-terraform-provider']
        for i in range(len(folder_names)):
            os.remove(os.getcwd() + '/' + str(i))
    except Exception as e:
        print("Error {} occurred while deleting folder {}".format(str(e), str(i)))

def createGitRepositories():
    # subprocess.check_call(["git", "clone", "https://github.com/HewlettPackard/oneview-python"])
    # subprocess.check_call(["git", "clone", "https://github.com/HewlettPackard/oneview-ansible-collections"])
    # subprocess.check_call(["git", "clone", "https://github.com/HewlettPackard/oneview-golang"])
    # subprocess.check_call(["git", "clone", "https://github.com/HewlettPackard/oneview-terraform-provier"])

if __name__ == '__main__':
    selected_sdk = sys.argv[1]
    api_version = sys.argv[2]
    #createGitRepositories()
    print("---------Started executing files---------")
    LOG_FILENAME = datetime.now().strftime('logfile_%H_%M_%d_%m_%Y.log')
    f = open(LOG_FILENAME, 'w')
    original = sys.stdout
    sys.stdout = LogWriter(f)
    os.system('python collectionsConfig.py -a "1.1.1.1" -u "Admin" -p "admin" -d "OVAD" -i "1.1.2.2" -v 3200 -w "Synergy" -l oneview-ansible-collection')
    resources_executor = executeResources.executeResources(selected_sdk, api_version)
    executed_files = resources_executor.execute(resource_dict)
    sys.stdout = original
    python_executor = executePythonResources.executePythonResources(resource_dict)
    resources_from_textfile = python_executor.load_resources()
    if len(executed_files) != len(resources_from_textfile):
        print("Didn't generate code in CHANGELOG.md as there are few failed_resources")
    else:
        print("---------Started writing to CHANGELOG.md---------")
        changelog_generator = changeLogGenerator.changeLogGenerator(executed_files)
        changelog_generator.write_data()
    #     print("---------Completed writing to CHANGELOG.md---------")
    #     endpointsfile_writer = writeEndPointsFile.writeEndpointsFile('## HPE OneView', executed_files)
    #     endpointsfile_writer.main()

    clean_up_files()
