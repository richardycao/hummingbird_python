import os

class Pipeline(object):
  def __init__(self, containers=[]):
    """
    modules : list of Module

    For now, the pipeline will just be a sequence of modules - no parallel modules.
    The pipeline will be created in the order that the modules come in.
    """

    self.containers = containers
    self.tab_size = 2

  def __tabs(self, count):
    tab = ''.join([' ' for _ in range(self.tab_size)])
    return ''.join([tab for _ in range(count)])

  def synthesize(self):
    """
    Create the docker files.
      - This is called from anywhere, as long as the path to each of the containers
        is provided.
      - The 'run' command in each Dockerfile should set its arguments based on arguments passed
        into this Pipeline object.

      
    """

    for c_path in self.containers:
      with open(c_path + "/Dockerfile", 'w') as f:
        f.write("FROM ubuntu:latest\n")
        f.write("\n")
        f.write("RUN apt-get update\n")
        f.write("RUN apt-get install -y python3.7 python3-pip python3-dev git\n")
        f.write("RUN pip3 install --upgrade pip\n")
        f.write("\n")
        f.write("WORKDIR /usr/src/app\n")
        f.write("COPY requirements.txt .\n")
        f.write("RUN pip3 install -r requirements.txt\n")
        f.write("\n")
        f.write("COPY *.py .\n")
        f.write("CMD python3 ") # doesn't work atm

    """
    Create the docker-compose file for the pipeline
    """

    with open('docker-compose-test.yml', 'w') as f:
      f.write("version: '3.7'\n")
      f.write("\n")
      f.write("services:\n")

      i = len(self.containers) - 1
      for dir in reversed(self.containers):
        label = "stage" + str(i)
        f.write(self.__tabs(1) + label + ":\n")
        f.write(self.__tabs(2) + "build: " + dir + "\n")
        f.write(self.__tabs(2) + "container_name: " + label + "\n")
        f.write(self.__tabs(2) + "depends_on:\n")

        # Very temporary way to set dependencies
        for j in range(i + 1, len(self.containers)):
          f.write(self.__tabs(3) + "- " + "stage" + str(j) + "\n")

        i -= 1

  def build(self):
    """
    Build the docker-compose files
    """

    # Build the docker compose for Kafka
    os.system('docker-compose -f docker-compose-kafka.yml build')

    # Build the docker compose for the pipeline
    os.system('docker-compose -f docker-compose-test.yml build')

  def run(self):
    # Maybe this part should be done manually. Leave it blank for now.

    # Run Kafka docker

    # Wait

    # Run pipeline docker

    pass
