from confluent_kafka import Producer, Consumer, KafkaException
import sys
import getopt
import json

"""
Base definition of a Module (for now):

1 input, 1 output - specified when pipeline.generate() is called, since that's when
                    the Dockerfiles (and hence, args for the command) and docker-compose
                    pipeline file are generated.
base args           - defined in this file. specified as input to Pipeline and set during 
                    pipeline.generate()
customs args        - defined when the creator defines their own custom Module. specified
                    as input to Pipeline and set during pipeline.generate()

What are the base args?
type                - input, output, both, or neither. Specified in the definition of the
                      custom module. can be 'i', 'o', 'io', or ''
topics_in           - auto-generated based on the pipeline
topics_out          - auto-generated based on the pipeline
servers_in          - kafka0:29092. Same as bootstrap.servers for the consumer
servers_out         - kafka0:29092. Same as bootstrap.servers for the producer
group.id            - auto-generated based on the pipeline. Not really sure what the point of
                    this is yet.
session.timeout.ms  - default is 10000
auto.offset.reset   - default is 'earliest'

When a module is created, all args (including the custom args) are specified at the
same time.

-----

For I/O parameters:

Each custom-made module should specify which inputs and outputs are required and/or optional.
Params are passed as messages in JSON form.
When a pipeline is generated, it should check if the I/O params are valid matches.

"""
class Module(object):
  def __init__(self, args):
    # Default base args
    self.args = {
      'topics_in'         : '',
      'topics_out'        : '',
      'servers_in'        : '',
      'servers_out'       : '',
      'group.id'          : 'test',
      'session.timeout.ms': 10000,
      'auto.offset.reset' : 'earliest'
    }
    
    short_options = ""
    long_options = ["topics-in=", "topics-out=", "servers-in=", "servers-out=",
                    "group-id=", "session-timeout-ms=", "auto-offset-reset="]

    try:
      arguments, _ = getopt.getopt(args, short_options, long_options)
      
      for currentArgument, currentValue in arguments:
        if currentArgument in ("--topics-in"):
          self.args['topics_in'] = currentValue.split(',')
        elif currentArgument in ("--topics-out"):
          self.args['topics_out'] = currentValue.split(',')
        elif currentArgument in ("--servers-in"):
          self.args['servers_in'] = currentValue.split(',')
        elif currentArgument in ("--servers-out"):
          self.args['servers_out'] = currentValue.split(',')
        elif currentArgument in ("--group-id"):
          self.args['group.id'] = currentValue
        elif currentArgument in ("--session-timeout-ms"):
          self.args['session.timeout.ms'] = int(currentValue)
        elif currentArgument in ("--auto-offset-reset"):
          self.args['auto.offset.reset'] = currentValue
                
    except getopt.error as err:
      print(str(err))

  def buildIO(self):
    if 'i' in self.args['type']:
      print('Creating consumer')
      conf_in = {
        'bootstrap.servers' : self.args['servers_in'][0],
        'group.id'          : self.args['group.id'],
        'session.timeout.ms': self.args['session.timeout.ms'],
        'auto.offset.reset' : self.args['auto.offset.reset']
      }
      self.consumer = Consumer(conf_in)
      self.consumer.subscribe(self.args['topics_in'])

    if 'o' in self.args['type']:
      print('Creating producer')
      conf_out = { 'bootstrap.servers': self.args['servers_out'][0] }
      self.producer = Producer(**conf_out)
  
  def delivery_callback(self, err, msg):
    if err:
      print('Delivery_callback failed delivery:', err)
      print(json.loads(msg))

  def run(self):
    pass