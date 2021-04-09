
class Node(object):
  def __init__(self, id, path, params={}, inputs=[], outputs=[]):
    self.id = id
    self.path = path
    self.params = params
    self.inputs = inputs
    self.outputs = outputs

