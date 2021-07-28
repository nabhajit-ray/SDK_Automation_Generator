from sdkAutomator.executeResources import executeResources
import os
import subprocess
import sys

class executeTerraformResources(executeResources):
    """
    To Execute Terraform SDK.

    """

    build_cmd = "go build -o terraform-provider-oneview"
    moving_binary_cmd1 = "mkdir -p ~/.terraform.d/plugins/"
    moving_binary_cmd2 = "mv terraform-provider-oneview ~/.terraform.d/plugins/"
    
    def __init__(self):
        super(executeTerraformResources).__init__(self)


    def run_terraform_executor(self):
        """
        Executor for Terraform modules
        """
        for example in self.exe:

            build = subprocess.Popen(self.build_cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
            build.wait()
            if build.poll() == 0:
                build = subprocess.Popen(self.moving_binary_cmd1, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                build = subprocess.Popen(self.moving_binary_cmd2, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                build_output, build_errors = build.communicate()
                if build_errors:
                    print(build_errors)
                    sys.exit()
                example_loc = os.getcwd() + '/examples/' + example + '/'
                init_cmd = "terraform init"
                init_p = subprocess.Popen(init_cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                print("running terraform init")
                init_p.wait()
                for i in range(3):
                    if i == 0:
                        copy = "cp " + example_loc + "main.tf " + os.getcwd()
                        copy_p = subprocess.Popen(copy, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True, stderr=subprocess.PIPE)
                        op, copy_errors = copy_p.communicate()
                        print(copy_p.returncode )
                        if copy_p.returncode != 0:
                            print("Error Detected", copy_errors)
                            continue
                        else:
                            if example == "enclosures" or example == "logical_interconnects" or example == "storage_pools":
                                print("executing import: ", example)
                                if example == "enclosures":
                                    enc_import = subprocess.Popen("terraform import oneview_enclosure.import_enc 0000A66101", stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                                    _, errors = enc_import.communicate()
                                elif example == "storage_pools":
                                    ss_import = subprocess.Popen("terraform import oneview_storage_pool.storage_pool CPG-SSD-AO", stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                                    _, errors = ss_import.communicate()
                                else:
                                    li_import  = subprocess.Popen("terraform import oneview_logical_interconnect.logical_interconnect Auto-LE-Auto-LIG", stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                                    _, errors = li_import.communicate()
                                if errors is None:
                                    self.success_files.append(example + " main.tf")
                                else:
                                    self.failed_files.append(example + " main.tf")
                                os.remove(os.getcwd() + "/main.tf")
                                continue
                            plan_cmd = "terraform plan"
                            print("executing main.tf plan: ", example)
                            _ = subprocess.Popen("terraform init", stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                            plan_p = subprocess.Popen(plan_cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                            plan_p.wait()
                            if plan_p.poll() == 0:
                                _, plan_errors = plan_p.communicate()
                                if plan_errors is None:
                                    apply_cmd = "terraform apply --auto-approve"
                                    print("executing main.tf apply: ", example)
                                    apply_p = subprocess.Popen(apply_cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                                    _, apply_errors = apply_p.communicate()
                                    apply_p.wait()
                                    os.remove(os.getcwd() + "/main.tf")
                                    if apply_errors != None:
                                        self.failed_files.append(example + " main.tf")
                                    else:
                                        self.success_files.append(example + " main.tf")
                                else:
                                    os.remove(os.getcwd() + "/main.tf")
                                    self.failed_files.append(example + " main.tf")
                            else:
                                os.remove(os.getcwd() + "/main.tf")
                                self.failed_files.append(example + " main.tf plan_p.poll is != 0, ") 
                    elif i == 1:
                        copy = "cp " + example_loc + "update_resource.tf " + os.getcwd()
                        copy_p = subprocess.Popen(copy, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True, stderr=subprocess.PIPE)
                        op, copy_errors = copy_p.communicate()
                        print( copy_p.returncode, copy_errors, "No Copy Errors")
                        if copy_p.returncode != 0:
                            print("Error Detected", copy_errors)
                            self.failed_files.append(example + " failed to copy update_resource file, ")
                            continue
                        else:
                            print("executing update_resource.tf plan: ", example)
                            plan_cmd = "terraform plan"
                            plan_p = subprocess.Popen(plan_cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                            plan_p.wait()
                            if plan_p.poll() == 0:
                                _, plan_errors = plan_p.communicate()
                                if plan_errors is None:
                                    print("executing update_resource.tf apply: ", example)
                                    apply_cmd = "terraform apply --auto-approve"
                                    apply_p = subprocess.Popen(apply_cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                                    apply_p.wait()
                                    _, apply_errors = apply_p.communicate()
                                    os.remove(os.getcwd() + "/update_resource.tf")
                                    if apply_errors != None:
                                        self.failed_files.append(example + " update_resource.tf")
                                    else:
                                        self.success_files.append(example + " update_resource.tf")
                                else:
                                    os.remove(os.getcwd() + "/update_resource.tf")
                                    self.failed_files.append(example + " update_resource.tf")
                            else:
                                os.remove(os.getcwd() + "/update_resource.tf")
                                self.failed_files.append(example + " update_resource.tf the plan_p.poll is != 0, ")
                    else:
                        copy = "cp " + example_loc + "data_source.tf " + os.getcwd()
                        copy_p = subprocess.Popen(copy, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                        _, copy_errors = copy_p.communicate()
                        if  copy_errors is None:
                            print("executing data_source.tf plan: ", example) 
                            if os.path.exists(os.getcwd() + "/terraform.tfstate"):
                                os.remove( os.getcwd() + "/terraform.tfstate")
                            if os.path.exists(os.getcwd() + "/terraform.tfstate.backup"):
                                os.remove(os.getcwd() + "/terraform.tfstate.backup")
                            plan_cmd = "terraform plan"
                            plan_p = subprocess.Popen(plan_cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                            plan_p.wait()
                            if plan_p.poll() == 0:
                                _, plan_errors = plan_p.communicate()
                                if plan_errors is None:
                                    print("executing data_source.tf apply: ", example) 
                                    apply_cmd = "terraform apply --auto-approve"
                                    apply_p = subprocess.Popen(apply_cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                                    apply_p.wait()
                                    _, apply_errors = apply_p.communicate()
                                    os.remove(os.getcwd() + "/data_source.tf")
                                    os.remove( os.getcwd() + "/terraform.tfstate")
                                    if os.path.exists(os.getcwd() + "/terraform.tfstate.backup"):
                                        os.remove(os.getcwd() + "/terraform.tfstate.backup")
                                    if apply_errors != None:
                                        self.failed_files.append(example + " data_source.tf")
                                    else:
                                        self.success_files.append(example + " data_source.tf")
                                else:
                                    os.remove(os.getcwd() + "/data_source.tf")
                                    self.failed_files.append(example + " data_source.tf")
                            else:
                                os.remove(os.getcwd() + "/data_source.tf")
                                self.failed_files.append(example + " data_source.tf the plan_p.poll is != 0, ") 
                        else:
                            self.failed_files.append(example + " failed to copy data_source file ")