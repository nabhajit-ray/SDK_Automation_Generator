from ansible_playbook_runner import Runner
import sys, os


class executeAnsibleResources(object):
    """
    To Execute Ansible SDK.

    """
    ansible_exe = []

    def __init__(self):
        executable_resources = self.read_ansible_resources(self)
    
    def read_ansible_resources(self):
        """
        Modifying ansible playbook names to make them uniform across all SDK's
        """
        os.chdir(os.getcwd() + '/ansible/playbooks')
        try:
            with open('automation.yaml', 'r') as ansible_modules_list:
                ansible_modules = ansible_modules_list.read().splitlines()
            if not ansible_modules:
                print("no data in file ansible_modules_list")

        except IOError as e:
            print ("I/O error({0}): {1}".format(e.errno, e.strerror))
        except:
            print("Unexpected error: {}", sys.exc_info()[0])

        return list(set(self.ansible_modules))

    def run_ansible_executor(self):
        """
        Executor for Ansible playbooks
        """
        success_files = []
        failed_files = []
        try:
            for executable in self.executable_resources:
                result = Runner(['/etc/ansible/hosts'], executable).run()
                if result == 0:
                    success_files.append(executable)
                else:
                    failed_files.append(executable)
        except Exception as e:
            print("Error while executing playbook {}".format(str(e)))
        
        return self.success_files
