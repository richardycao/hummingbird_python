import os
from pathlib import Path

class Pipeline(object):
  def __init__(self, id, modules=[]):
    """
    modules: list of PipelineNode
    """
    self.id = id
    self.modules = modules
    self.tab_size = 2

  def __tabs(self, count):
    tab = ''.join([' ' for _ in range(self.tab_size)])
    return ''.join([tab for _ in range(count)])

  def parse_params(self, io, params, path=''):
    for key, value in params.items():
      if isinstance(value, dict):
        self.parse_params(io, value, path=key+'/')
      else:
        io.write(" --" + path + str(key) + " " + value)

  def build(self):
    """
    Create the docker files.
      - This is called from anywhere, as long as the path to each of the containers
        is provided.
      - The 'run' command in each Dockerfile should set its arguments based on arguments passed
        into this Pipeline object.

    What info is needed about the paths?
    - the relative path from the root directory is need for docker-compose.yml
    - the main python file to run
    - the name of the container - should be the directory name, which is included
      in the path
      
    """
    queue_count = 0
    for module in self.modules:
      path = Path(module.module_path)
      with open(str(path.parent) + "/Dockerfile", 'w') as f:
        f.write("FROM ubuntu:latest\n")
        f.write("\n")
        f.write("RUN apt-get update\n")
        f.write("RUN apt-get install -y python3.7 python3-pip python3-dev\n")
        f.write("RUN apt-get install -y git\n")
        f.write("RUN pip3 install --upgrade pip\n")
        f.write("\n")
        f.write("WORKDIR /usr/src/app\n")
        f.write("COPY requirements.txt .\n")
        f.write("RUN pip3 install -r requirements.txt\n")

        # I'm not sure why it isn't upgrading. uninstall -> reinstall is the temporary fix
        f.write("RUN pip3 uninstall hummingbird\n")
        f.write("RUN pip install --upgrade git+https://github.com/richardycao/hummingbird_python.git#egg=hummingbird\n")
        f.write("\n")
        f.write("COPY *.py .\n")
        f.write("CMD python3 " + path.name)

        # Generating kafka I/O params and writing them to the python command
        f.write(" --topics-in " + str(self.id) + "-" + str(queue_count))
        f.write(" --topics-out " + str(self.id) + "-" + str(queue_count + 1))

        # Writing other params to the python command
        params = module.params
        for key, value in params.items():
          f.write(" --" + key + " " + value)
        f.write("\n")
        #self.parse_params(f, params)

        queue_count += 1

    """
    Create the docker-compose file for the pipeline
    """

    with open('./docker-compose-' + str(self.id) + '.yml', 'w') as f:
      f.write("version: '3.7'\n")
      f.write("\n")
      f.write("services:\n")

      dependencies = []
      for module in reversed(self.modules):
        path = Path(module.module_path)
        label = path.parent.name
        f.write(self.__tabs(1) + label + ":\n")
        f.write(self.__tabs(2) + "build: " + str(path.parent) + "\n")
        f.write(self.__tabs(2) + "container_name: " + label + "\n")
        f.write(self.__tabs(2) + "environment:\n")
        f.write(self.__tabs(3) + "- \"PYTHONUNBUFFERED=1\"\n")
        if len(dependencies) > 0:
          f.write(self.__tabs(2) + "depends_on:\n")

        # Very temporary way to set dependencies
        for dep in dependencies:
          f.write(self.__tabs(3) + "- " + dep + "\n")

        dependencies.append(label)

    """
    Build the docker-compose files
    """

    # Build the docker compose for Kafka
    os.system('docker-compose -f docker-compose-kafka.yml build')

    # Build the docker compose for the pipeline
    os.system('docker-compose -f docker-compose-' + str(self.id) + '.yml build')

  def run(self):
    # Maybe this part should be done manually. Leave it blank for now.

    # Run Kafka docker

    # Wait

    # Run pipeline docker

    pass
