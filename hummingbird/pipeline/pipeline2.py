import os
import json
from pathlib import Path

"""
Example:

Pipeline(
  id = 'test-id',
  nodes = {
    Node(
      id = 'node1',
      path = './module1',
      params = {},
      inputs = [],
      outputs = ['node2']
    ),
    Node(
      id = 'node2',
      path = './module2',
      params = {},
      inputs = ['node1'],
      outputs = []
    ),
  }
)

"""

class Pipeline2(object):
  def __init__(self, id, nodes=[]):
    self.id = id
    self.nodes = nodes
    self.tab_size = 2

  def __tabs(self, count):
    tab = ''.join([' ' for _ in range(self.tab_size)])
    return ''.join([tab for _ in range(count)])

  def parse_settings(self, path):
    # Default settings
    settings = {
      'use_custom_dockerfile': False
    }

    path = str(path.parent)
    with open(path + "/settings.txt", 'r') as f:
      line = f.readline().strip()
      while line:
        pair = line.split("=")
        if pair[0].strip() == "use_custom_dockerfile":
          settings['use_custom_dockerfile'] = bool(pair[1].strip())
        line = f.readline().strip()
    return settings

  def export_params(self, node, path):
    params = node.params
    if "topics_in" not in params:
      params["topics_in"] = [i + "-" + node.id for i in node.inputs]
    if "topics_out" not in params:
      params["topics_out"] = [node.id + "-" + o for o in node.outputs]
    if "servers_in" not in params:
      params["servers_in"] = "kafka:29092"
    if "servers_out" not in params:
      params["servers_out"] = "kafka:29092"
    if "session_timeout_ms" not in params:
      params["session_timeout_ms"] = 1000
    if "auto_offset_reset" not in params:
      params["auto_offset_reset"] = "earliest"
    if "group_id" not in params:
      params["group_id"] = self.id

    path = str(path.parent)
    with open(path + "/params.json", 'w') as f: 
      json.dump(params, f)

  def generate_dockerfile(self, path):
    with open(str(path.parent) + "/Dockerfile", 'w') as f:
      f.write("FROM ubuntu:latest\n")
      f.write("\n")
      f.write("RUN apt-get update\n")
      f.write("RUN apt-get install -y python3.7 python3-pip python3-dev\n")
      f.write("RUN apt-get install -y git\n")
      f.write("RUN pip3 install --upgrade pip\n")
      f.write("\n")
      f.write("WORKDIR /usr/src/app\n")
      f.write("COPY . .\n")
      f.write("RUN pip3 install -r requirements.txt\n")

      # I'm not sure why it isn't upgrading. uninstall -> reinstall is the temporary fix
      f.write("RUN pip3 uninstall hummingbird\n")
      f.write("RUN pip3 install --upgrade git+https://github.com/richardycao/hummingbird_python.git#egg=hummingbird\n")
      f.write("\n")
      f.write("CMD python3 " + path.name)

  def generate_docker_compose(self, path):
    with open('./docker-compose-' + str(self.id) + '.yml', 'w') as f:
      f.write("version: '3.7'\n")
      f.write("\n")
      f.write("services:\n")

      for node in reversed(self.nodes):
        path = Path(node.path)
        container_name = node.id
        f.write(self.__tabs(1) + container_name + ":\n")
        f.write(self.__tabs(2) + "build: " + str(path.parent) + "\n")
        f.write(self.__tabs(2) + "container_name: " + container_name + "\n")
        f.write(self.__tabs(2) + "environment:\n")
        f.write(self.__tabs(3) + "- \"PYTHONUNBUFFERED=1\"\n")
        if len(node.outputs) > 0:
          f.write(self.__tabs(2) + "depends_on:\n")

        for output_id in node.outputs:
          f.write(self.__tabs(3) + "- " + output_id + "\n")

  def build(self):
    for node in self.nodes:
      path = Path(node.path)
      settings = self.parse_settings(path) # Does this work if there isn't a settings file?
      self.export_params(node, path)

      if not settings['use_custom_dockerfile']:
        self.generate_dockerfile(path)

      self.generate_docker_compose(path)

    os.system('docker-compose -f docker-compose-kafka.yml build')
    os.system('docker-compose -f docker-compose-' + str(self.id) + '.yml build')

  def run(self):
    # Maybe this part should be done manually. Leave it blank for now.

    # Run Kafka docker

    # Wait

    # Run pipeline docker

    pass
