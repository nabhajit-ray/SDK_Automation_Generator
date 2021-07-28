import executeResources
import os, sys
import shutil

class executePythonResources():

    exe = []

    """
    To Execute Python SDK.

    """
    
    def __init__(self, resource_dict):
        self.resource_dict = resource_dict
        self.exe = self.load_resources()

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
            exit()
        except Exception as e:
            print("Unexpected error: {}".format(str(e)))
            exit()

        return self.exe

    def run_python_executor(self):
        """
        Executor for Python modules
        """
        for example in self.exe:
            example_file = os.getcwd() + '/oneview-' + self.selected_sdk + '/examples/' + example + str('.py')
            try:
                print(">> Executing {}..".format(example))
                exec(compile(open(example_file).read(), example_file, 'exec'))
                self.success_files.append(example)    
            except Exception as e:
                print("Failed to execute {} with exception {}".format(str(example),(str(e))))
                self.failed_files.append(example)
            finally:
                os.remove(os.getcwd() + '/oneview-' + self.selected_sdk + '/examples/config.json')
                shutil.copyfile(os.getcwd() + '/oneview-' + self.selected_sdk + '/examples/config-rename_dummy.json', os.getcwd() + '/oneview-' + self.selected_sdk + '/examples/config-rename.json')
                os.remove(os.getcwd() + '/oneview-' + self.selected_sdk + '/examples/config.json')
        return self.success_files
