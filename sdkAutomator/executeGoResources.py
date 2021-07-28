from sdkAutomator.executeResources import ExecuteResources
import os
import subprocess
import sys

class ExecuteGoResources(ExecuteResources):
    """
    To Execute GoLang SDK.

    """
    
    def __init__(self):
        super(ExecuteGoResources).__init__(self)

    def run_go_executor(self):
        """
        Executor for Go modules
        """
        for example in self.exe:
            example_file = os.getcwd() + '/golang/' + example + str('.go')
            try:
                cmd = "go run {}".format(example_file)
                res = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                res.wait()
                contents = res.stdout.read()
                print(contents)
                output, errors = res.communicate()
                if output:
                    print("ret> {}", format(str(res.returncode)))
                    print("OK> output {}", format(str(output)))
                    self.success_files.append(example)
                if errors:
                    self.failed_files.append(example)
            except OSError as e:
                print("OSError > {} ",format(str(e.errno)))
                print("OSError > {}", format(str(e.strerror)))
                print("OSError > ", format(str(e.filename)))
            except:
                print("Error > {}", format(str(sys.exc_info()[0])))
        return self.success_files
