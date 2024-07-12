from flask_restful import fields

message_fields = {
  'cod': fields.Integer,
  'message': fields.String,
}


class Message():
  def __init__(self, message, cod):
    self.cod = cod
    self.message = message