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
        cmd = "python collection_config.py -a 1.1.1.1 -u Admin -p admin -d OVAD -i 1.1.2.2 -v 3200 -w Synergy -l oneview-ansible-collection"
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
            p.wait()
            contents = p.stdout.read()
            print(contents)
            output, errors = p.communicate()
            if errors is  None:
                print("Config update went successful")
        except Exception as e:
            print("Error while updating configuration {}".formart(str(e)))

    def run_ansible_executor(self):
        """
        Executor for Ansible playbooks
        """
        try:
            os.chdir('/home/venkatesh/oneview-ansible-collection/playbooks')
            result = Runner(['/etc/ansible/hosts'], 'automation.yml').run()
            if result == 0:
                print("Executor for Ansible playbooks went successful")
        except Exception as e:
            print("Error while executing playbook {}".format(str(e)))
        finally:
            cmd = 'python collection_config.py'
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
            p.wait()
            contents = p.stdout.read()
            print(contents)
            output, errors = p.communicate()
            if errors:
                os.chdir(os.getcwd())
                raise Exception('error in post cleanup actions in run_ansible_executor')
            os.chdir(os.getcwd())
        
        return self.success_files
