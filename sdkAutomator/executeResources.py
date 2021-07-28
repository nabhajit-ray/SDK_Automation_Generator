from sdkAutomator.resource import Resource
from sdkAutomator.executeAnsibleResources import ExecuteAnsibleResources
from sdkAutomator.executePythonResources import ExecutePythonResources
from sdkAutomator.executeGoResources import ExecuteGoResources
from sdkAutomator.executeTerraformResources import ExecuteTerraformResources
import sys, os, json, shutil


class ExecuteResources(Resource):

    exe = []

    def __init__(self, selected_sdk, api_version):
        super(ExecuteResources).__init__(self, selected_sdk, api_version)
        self.load_resources()
        self.generate_config_values(self)
        self.success_files = []
        self.failed_files = []

    def generate_config_values(self):
        shutil.copyfile(os.getcwd() + self.selected_sdk + 'config-rename.json', os.getcwd() + self.selected_sdk + 'config-rename_dummy.json')
        os.rename(os.getcwd() + self.selected_sdk + 'config-rename.json', os.getcwd() + self.selected_sdk + 'config.json')
        with open(os.getcwd() + self.selected_sdk + 'config.json', 'r') as config:
            json_object = json.load(config)
            json_object["ip"] = ""
            json_object["credentials"]["userName"] = ""
            json_object["credentials"]["password"] = ""
            json_object["credentials"]["userName"] = ""
            json_object["image_streamer_ip"] = ""
            json_object["api_version"] = ""
            json_object["server_certificate_ip"] = "172.18.13.11"
            json_object["hypervisor_manager_ip"] = "172.18.13.11"
            json_object["hypervisor_user_name"] = "dcs"
            json_object["hypervisor_password"] = "dcs"
            json_object["storage_system_hostname"] = ""
            json_object["storage_system_username"] = ""
            json_object["storage_system_password"] = ""
            json_object["storage_system_family"] = ""
            with open(os.getcwd() + self.selected_sdk + 'config.json', 'w') as config:
                json.dump(json_object, config)
    
    def load_resources(self):
        """
        To load resources(examples) from external config file.
        """
        try:
            with open('../resources_list.txt', 'r') as resources_list:
                resources = resources_list.read().splitlines()
            if not resources:
                print("no data in file resources_list")

        except IOError as e:
            print ("I/O error({0}): {1}".format(e.errno, e.strerror))
        except:
            print("Unexpected error: {}", sys.exc_info()[0])

        for resource in self.resources_list:
            self.exe.append(self.resource_dict[resource])

        return self.exe
    
    def execute(self):
        if self.selected_sdk == 'python':
            executed_files = ExecutePythonResources.run_python_executor(self)
        elif self.selected_sdk == 'ansible':
            executed_files = ExecuteAnsibleResources.run_ansible_executor(self)
        elif self.selected_sdk == 'go' or self.selected_sdk == 'golang':
            executed_files = ExecuteGoResources.run_go_executor()
        elif self.selected_sdk == 'terraform':
            executed_files = ExecuteTerraformResources.run_terraform_executor()
        else:
            print("Invalid SDK")
    
        return executed_files
    
