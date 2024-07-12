from flask_restful import fields
from helpers.database import db

doacaoCampanha_fields = {
  'id' : fields.Integer,
  'nome': fields.String,
  'email': fields.String,
  'cpf': fields.String,
  'numConta': fields.String,
  'valor' : fields.Float,
  'doador_id' : fields.Integer,
  'campanha_id' : fields.Integer,
}

historico_doacoes_fields = {
    'campanha_id': fields.Integer,
    'campanha_titulo': fields.String,
    'doador_id': fields.Integer,
    'doador_nome': fields.String,
    'valor': fields.Float
}

class DoacaoCampanha(db.Model):
  __tablename__ = "doacaoCampanha"

  id = db.Column(db.Integer, primary_key=True)

  valor = db.Column(db.Float, nullable=False)
  nome = db.Column(db.String, nullable=False)
  email = db.Column(db.String, nullable=False)
  cpf = db.Column(db.String, nullable=False)
  numConta = db.Column(db.String, nullable=False)

  campanha_id = db.Column(db.Integer, db.ForeignKey('campanha.id'), nullable=False)
  doador_id = db.Column(db.Integer, db.ForeignKey('doador.id_pessoa'), nullable=False)

  # campanha = db.relationship("Campanha", backref=db.backref("doacao", uselist=False))
  doador = db.relationship("Doador", backref="doacoes", lazy=True)

  def __init__(self, valor, campanha_id, nome, email, cpf, numConta, doador_id):
    self.valor = valor
    self.campanha_id = campanha_id
    self.nome = nome
    self.email = email
    self.cpf = cpf
    self.numConta = numConta
    self.doador_id = doador_id

  def __repr__(self):
    return f'<Doar {self.id}>'
