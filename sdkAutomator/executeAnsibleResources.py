from ansible_playbook_runner import Runner
import os
import subprocess


class executeAnsibleResources(object):
    """
    To Execute Ansible SDK.

    """

    def __init__(self):
        self.prepare_environment_for_ansible_collections()

    def prepare_environment_for_ansible_collections(self):
        cmd = "python collectionConfig.py -a 10.1.19.63 -u Administrator -p admin123 -d local -v 3200 -w Synergy -l /home/venkatesh/Documents/oneview-ansible-collection"
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
            p.wait()
            contents = p.stdout.read()
            print(contents)
            output, errors = p.communicate()
            if errors is None:
                print("Config update went successful")
        except Exception as e:
            print("Error while updating configuration {}".formart(str(e)))

    def run_ansible_executor(self):
        """
        Executor for Ansible playbooks
        """
        cwd = os.getcwd()
        try:

            os.chdir('/home/venkatesh/Documents/oneview-ansible-collection/playbooks/')
            result = Runner(['/etc/ansible/hosts'], 'automation.yaml').run()
            if result == 0:
                print("Executor for Ansible playbooks went successful")
                return True
            else:
                return False
        except Exception as e:
            print("Error while executing playbook {}".format(str(e)))
        finally:
            os.chdir(cwd)
            cmd = 'python collectionConfig.py -l /home/venkatesh/Documents/oneview-ansible-collection'
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
            p.wait()
            contents = p.stdout.read()
            print(contents)
            output, errors = p.communicate()
            if errors:
                os.chdir(cwd)
                raise Exception('error in post cleanup actions in run_ansible_executor')
            os.chdir(cwd)
            return