from confluent_kafka import Producer, Consumer, KafkaException
import sys
import getopt
import json

"""
Base definition of a Module (for now):

1 input, 1 output - specified when pipeline.synthesize() is called, since that's when
                    the Dockerfiles (and hence, args for the command) and docker-compose
                    pipeline file are synthesized.
base args           - defined in this file. specified as input to Pipeline and set during 
                    pipeline.synthesize()
customs args        - defined when the creator defines their own custom Module. specified
                    as input to Pipeline and set during pipeline.synthesize()

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
When a pipeline is synthesized, it should check if the I/O params are valid matches.

"""
class Module(object):
  def __init__(self, args):
    self.input_args = args
    # Default base args
    self.args = {
      # These are defined in the module implementation
      'has_input'         : False,
      'has_output'        : False,
      # These can be set by the user
      'session_timeout_ms': 10000,
      'auto_offset_reset' : 'earliest',
      # These will be generated during pipeline.synthesize()
      'topics_in'         : '',
      'topics_out'        : '',
      'servers_in'        : 'kafka0:29092',
      'servers_out'       : 'kafka0:29092',
      'group_id'          : 'test'
    }
    self.custom_options = {}
  
  def setInput(self, val: bool):
    self.args['has_input'] = val

  def setOutput(self, val: bool):
    self.args['has_output'] = val

  def add_argument(self, option, parser=None):
    self.custom_options[option] = parser

  def build(self):
    short_options = ""
    long_options = ["topics-in=", "topics-out=", "servers-in=", 
                    "servers-out=", "group-id=", "session-timeout-ms=", 
                    "auto-offset-reset="] + list(map(
                      lambda x: (x + '=') if self.custom_options[x] != None else x,
                      self.custom_options.keys()
                    ))

    try:
      arguments, _ = getopt.getopt(self.input_args, short_options, long_options)
      
      for currentArgument, currentValue in arguments:
        if currentArgument in ("--topics-in"):
          self.args['topics_in'] = currentValue.split(',')
        elif currentArgument in ("--topics-out"):
          self.args['topics_out'] = currentValue.split(',')
        elif currentArgument in ("--servers-in"): # comma-separated
          self.args['servers_in'] = currentValue
        elif currentArgument in ("--servers-out"): # comma-separated
          self.args['servers_out'] = currentValue
        elif currentArgument in ("--group-id"):
          self.args['group_id'] = currentValue
        elif currentArgument in ("--session-timeout-ms"):
          self.args['session_timeout_ms'] = int(currentValue)
        elif currentArgument in ("--auto-offset-reset"):
          self.args['auto_offset_reset'] = currentValue
        else:
          # Check through all of the custom options
          for cop in self.custom_options.keys():
            if currentArgument in ("--" + cop):
              if self.custom_options[cop]:
                self.args[cop] = self.custom_options[cop](currentValue)
              else:
                pass # depends
                
    except getopt.error as err:
      print(str(err))

    if self.args['has_input']:
      print('Creating consumer')
      conf_in = {
        'bootstrap.servers' : self.args['servers_in'],
        'group.id'          : self.args['group_id'],
        'session.timeout.ms': self.args['session_timeout_ms'],
        'auto.offset.reset' : self.args['auto_offset_reset']
      }
      self.consumer = Consumer(conf_in)
      self.consumer.subscribe(self.args['topics_in'][0])

    if self.args['has_output']:
      print('Creating producer')
      conf_out = { 'bootstrap.servers': self.args['servers_out'] }
      self.producer = Producer(**conf_out)
  
  def delivery_callback(self, err, msg):
    if err:
      print('Delivery_callback failed delivery:', err)
      print(json.loads(msg))

  def run(self):
    pass