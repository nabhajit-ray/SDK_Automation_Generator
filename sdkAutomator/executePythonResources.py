from sdkAutomator.executeResources import ExecuteResources
import os
import shutil

class ExecutePythonResources(ExecuteResources):
    """
    To Execute Python SDK.

    """
    
    def __init__(self):
        super(ExecutePythonResources).__init__(self)

    def run_python_executor(self):
        """
        Executor for Python modules
        """
        for example in self.exe:
            example_file = os.getcwd() + self.selected_sdk + example + str('.py')
            try:
                print(">> Executing {}..".format(example))
                exec(compile(open(example_file).read(), example_file, 'exec'))
                self.success_files.append(example)    
            except Exception as e:
                print("Failed to execute {} with exception {}".format(str(example),(str(e))))
                self.failed_files.append(example)
            finally:
                os.remove(os.getcwd() + self.selected_sdk + 'config.json')
                shutil.copyfile(os.getcwd() + self.selected_sdk + 'config-rename_dummy.json', os.getcwd() + self.selected_sdk + 'config-rename.json')
                os.remove(os.getcwd() + self.selected_sdk + 'config.json')
        return self.success_files