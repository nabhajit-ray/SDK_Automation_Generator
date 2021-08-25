#sudo chmod 666 /var/run/docker.sock
# Run above command to run docker commands in non-admin mode

import docker     # pip install docker
import subprocess
import time
import os

image_name = "oneview-sdk-for-python-ci-cd"
command = "python examples/fc_networks.py"
try:
    client = docker.from_env()

    # building the base image
    subprocess.call("docker build -t {} .".format(str(image_name)), shell=True)

except Exception as e:
    print("Exception {} occurred while building an image".format(str(e)))

# sleeping for 30 secs
time.sleep(30)

# create and run container
#container = client.containers.run(image_name, command, detach=False, stdout=False, stderr=True, name= image_name)
container = client.containers.run(image_name, command, detach=True, name= image_name)
print(str(container))

# run container
result = container.exec_run(cmd = 'python examples/fc_networks.py', stream=False)
print(str(result))

f = open('output.txt', 'w')
f.write(str(result))

file_to_read = open("output.txt", "r")
data = file_to_read.read()
occurrences = data.count("Exception")
if (occurrences >= 1):
    print("Docker Image is not functional")

# stop and remove containers
container.stop()
container.remove()
