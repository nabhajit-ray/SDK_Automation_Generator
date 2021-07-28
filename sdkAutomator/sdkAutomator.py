
import fnmatch
import sys
import os
from datetime import datetime
import git
from sdkAutomator.executeResources import ExecuteResources
from sdkAutomator.changeLogGenerator import ChangeLogGenerator
from sdkAutomator.writeEndPointsFile import WriteToEndpointsFile

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

def removeLogFiles():
    print("---------Removing all log files---------------")
    for rootDir, subdirs, filenames in os.walk(os.getcwd()):
        for filename in fnmatch.filter(filenames, 'logfile*.log'):
            try:
                os.remove(os.path.join(rootDir, filename))
            except OSError:
                print("Error while deleting file")
                print("---------Completed removing log files--------------")

def createGitRepositories():
    git.Repo.clone_from('https://github.com/HewlettPackard/oneview-python', os.getcwd() + 'python')
    git.Repo.clone_from('https://github.com/HewlettPackard/oneview-ansible-collection', os.getcwd() + 'ansible')
    git.Repo.clone_from('https://github.com/HewlettPackard/oneview-golang', os.getcwd() + 'golang')
    git.Repo.clone_from('https://github.com/HewlettPackard/oneview-terraform-provider', os.getcwd() + 'terraform')

if __name__ == '__main__':
    selected_sdk = sys.argv[1]
    api_version = sys.argv[2]
    createGitRepositories()
    print("---------Started executing files---------")
    LOG_FILENAME = datetime.now().strftime('logfile_%H_%M_%d_%m_%Y.log')
    f = open(LOG_FILENAME, 'w')
    original = sys.stdout
    sys.stdout = LogWriter(f)
    resources_executor = ExecuteResources(selected_sdk, api_version)
    executed_files = resources_executor.execute(selected_sdk)
    # if selected_sdk == 'go':
    #     value_updated = input("\nPlease provide \"true\" as input if below mentioned example have variable updated with described values as below else provide \"false\" as input to terminate\n\nexamples/server_certificate.go\n\tserver_certificate_ip\t= \"172.18.11.11\"\nexamples/hypervisor_managers.go\n\thypervisor_manager_ip\t= \"172.18.13.11\"//\"<hypervisor_manager_ip>\"\n\tusername\t= \"dcs\" //\"<hypervisor_user_name>\"\n\tpassword\t= \"dcs\" //\"<hypervisor_password>\"\nexamples/storage_systems.go\n\tusername\t=\"dcs\"\n\tpassword\t=\"dcs\"\n\thost_ip \t=\"172.18.11.11\"\n\thost2_ip\t=\"172.18.11.12\"\n>>")
    #     if value_updated.lower() == 'false':
    #         sys.exit()
    sys.stdout = original
    resources_from_textfile = ExecuteResources.load_resources()
    if len(executed_files) != len(resources_from_textfile):
        print("Didn't generate code in CHANGELOG.md as there are few failed_resources")
    else:
        print("---------Started writing to CHANGELOG.md---------")
        changelog_generator = ChangeLogGenerator(executed_files)
        changelog_generator.write_data()
        print("---------Completed writing to CHANGELOG.md---------")
        endpointsfile_writer = WriteToEndpointsFile('## HPE OneView', executed_files)
        endpointsfile_writer.main()

    removeLogFiles()