from flask_restful import fields

login_fields = {
  'token': fields.String,
  'tipo': fields.String
}


class LoginModel():
  def __init__(self, token, tipo):
    self.token = token
    self.tipo = tipo