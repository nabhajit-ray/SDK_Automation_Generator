import os, json
import shutil

class executePythonResources():

    exe = []

    """
    To Execute Python SDK.

    """
    config_rename_file = os.getcwd() + '/oneview-python/examples/config-rename.json'
    config_rename_dummy_file = os.getcwd() + '/oneview-python/examples/config-rename_dummy.json'
    config_file = os.getcwd() + '/oneview-python/examples/config.json'

    def __init__(self, resource_dict):
        shutil.copyfile(self.config_rename_file, self.config_rename_dummy_file)
        self.resource_dict = resource_dict
        self.exe = self.load_resources()
        self.generate_config_values()

        
    def load_resources(self):
        """
        To load resources(examples) from external config file.
        """
        try:
            with open('../resource_list.txt', 'r') as resources_list:
                resources = resources_list.read().splitlines()
                print(str(resources))
                if not resources:
                    print("no data in file resourceslist")
                else:
                    for resource in resources:
                        if resource != '':
                            self.exe.append(self.resource_dict[resource])

        except IOError as e:
            print ("I/O error while loading resources from resources_list file({0}): {1}".format(e.errno, e.strerror))
            # remove files
            exit()
        except Exception as e:
            print("Unexpected error: {}".format(str(e)))
            # remove files
            exit()

        return self.exe

    def generate_config_values(self):
        check = self.check_validate_config(self.config_rename_file)
        if check:
            shutil.copyfile(self.config_rename_file, self.config_rename_dummy_file)
            os.rename(self.config_rename_file, self.config_file)
            try:
                with open(self.config_file, 'r') as config:
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
                    with open(self.config_file, 'w') as config:
                        json.dump(json_object, config)
            except Exception as e:
                print("Error {} occurred while generating config files". format(str(e)))
                if self.check_validate_config(self.config_file):
                    os.remove(self.config_file)
                    shutil.copyfile(self.config_rename_dummy_file, self.config_rename_file)

    def check_validate_config(self, file_name):
        return os.path.isfile(file_name)

    def run_python_executor(self):
        """
        Executor for Python modules
        """
        for example in self.exe:
            example_file = os.getcwd() + '/oneview-python/examples/' + example + str('.py')
            try:
                print(">> Executing {}..".format(example))
                exec(compile(open(example_file).read(), example_file, 'exec'))
                self.success_files.append(example)    
            except Exception as e:
                print("Failed to execute {} with exception {}".format(str(example),(str(e))))
                self.failed_files.append(example)
            finally:
                os.remove(self.config_file)
                shutil.copyfile(self.config_rename_dummy_file, self.config_rename_file)
        return self.success_files
