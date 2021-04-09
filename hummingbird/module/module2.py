from confluent_kafka import Producer, Consumer, KafkaException
import json

class Module2(object):
  def __init__(self):
    self.params = {}

    with open('params.json', 'r') as f:
      self.params = json.loads(f.read())

    # Set up consumer for all input topics
    if len(self.params['topics_in']) > 0:
      conf_in = {
        'bootstrap.servers' : self.params['servers_in'],
        'group.id'          : self.params['group_id'],
        'session.timeout.ms': self.params['session_timeout_ms'],
        'auto.offset.reset' : self.params['auto_offset_reset']
      }
      self.consumer = Consumer(conf_in)
      for i in self.params['topics_in']:
        self.consumer.subscribe(i)

    # Set up general producer for output
    if len(self.params['topics_out']) > 0:
      conf_out = { 'bootstrap.servers': self.params['servers_out'] }
      self.producer = Producer(**conf_out)
  
  def delivery_callback(self, err, msg):
    if err:
      print('Delivery_callback failed delivery:', err)
      print(json.loads(msg))

  def receive(self, timeout=1.0, decode=True):
    if len(self.params['topics_in']) > 0:
      msg = self.consumer.poll(timeout=timeout)

      if msg is None:
        return None
      if msg.error():
        raise KafkaException(msg.error())
      else:
        message = json.loads(msg.value().decode("utf-8")) if decode else msg
        return message
    
    return None

  def send(self, message, encode=True):
    if len(self.params['topics_out']) > 0:
      for j in self.params['topics_out']:
        self.producer.produce(j, value=json.dumps(message).encode('utf-8') if encode else message, callback=self.delivery_callback)
        self.producer.poll(0)

  def closeIO(self):
    if len(self.params['topics_in']) > 0:
      self.consumer.close()
    if len(self.params['topics_out']) > 0:
      self.producer.flush()

  def run(self):
    pass