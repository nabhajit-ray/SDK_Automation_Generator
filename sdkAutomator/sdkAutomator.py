
import fnmatch
import executePythonResources
import writeEndPointsFile
import executeResources
import changeLogGenerator
import sys
import os
import shutil
from datetime import datetime
import git # if git module is not found, use 'pip install gitpython'
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

def createGitRepositories(selected_sdk):
    git_url = 'https://github.com/HewlettPackard/oneview' + str(selected_sdk)
    repo = git.Repo.clone_from(git_url,
                           os.getcwd() + '/' + str(selected_sdk) + '/')
    return repo

def createFeatureBranch(repo, branchName):
    remote_branches = []
    num = 0
    for ref in repo.git.branch('-r').split('\n'):
        remote_branches.append(ref.replace(" ", ""))
        
    branch_present = True if 'origin/' + branchName in remote_branches else False
    if branch_present:
        branchName = branchName + '_' + str(num)
        num = num + 1
        createFeatureBranch(repo, branchName)
    else:
        new_branch = repo.create_head(branchName)
        new_branch.checkout()
    return branchName

if __name__ == '__main__':
    selected_sdk = sys.argv[1]
    api_version = sys.argv[2]
    #repo = createGitRepositories(selected_sdk)
    #branchName = createFeatureBranch(repo, 'feature')
    print("---------Started executing files---------")
    # LOG_FILENAME = datetime.now().strftime('logfile_%H_%M_%d_%m_%Y.log')
    # f = open(LOG_FILENAME, 'w')
    # original = sys.stdout
    # sys.stdout = LogWriter(f)
    resources_executor = executeResources.executeResources(selected_sdk, api_version)
    executed_files = resources_executor.execute(resource_dict)
    # sys.stdout = original
    if executed_files:
        print("---------Started writing to CHANGELOG.md---------")
        changelog_generator = changeLogGenerator.changeLogGenerator(resource_dict, api_version)
        changelog_generator.write_data()
        print("---------Completed writing to CHANGELOG.md---------")
        endpointsfile_writer = writeEndPointsFile.writeEndpointsFile('## HPE OneView', resource_dict, api_version)
        endpointsfile_writer.main()

    repo.git.add(A=True)
    repo.git.commit('-m', 'PR for reelase changes #pr',
                    author='chebroluharika@gmail.com') # to commit changes
    repo.git.push('--set-upstream', 'origin', branchName)
    repo.close()
    os.chdir(path) # Navigate to parent directory
    # Delete git cloned directory as cleanup
    if os.path.exists(os.getcwd() + '/' + str(selected_sdk)):
        shutil.rmtree(os.getcwd() + '/' + str(selected_sdk) + '/', ignore_errors=True)

    # clean_up_files()
