from flask_restful import fields
from helpers.database import db
from model.atleta import *
from datetime import datetime

campanha_fields = {
  'id': fields.Integer,
  'titulo': fields.String,
  'descricao': fields.String,
  'numero_time': fields.Integer,
  'meta_arrecadacao': fields.Float,
  'valor_arrecadado': fields.Float,
  'conta_destino': fields.String,
  'atleta_id': fields.Integer,
  'created_at': fields.DateTime
}

campanhasFieldsPagination = {
  "campanhas": fields.Nested(campanha_fields),
  "meta": {
    "itemsPorPagina": fields.Integer,
    "indiceDaPagina": fields.Integer,
    "totalCampanhas": fields.Integer
  }
}

class Campanha(db.Model):
  __tablename__ = "campanha"

  id = db.Column(db.Integer, primary_key=True)
  titulo = db.Column(db.String, nullable=False)
  descricao = db.Column(db.String, nullable=False)
  numero_time =  db.Column(db.Integer, nullable=False)
  meta_arrecadacao = db.Column(db.Float, nullable=False)
  valor_arrecadado = db.Column(db.Float, nullable=False)
  conta_destino = db.Column(db.String, nullable=False)
  atleta_id = db.Column(db.Integer, db.ForeignKey('atleta.id_pessoa'), nullable=True)
  created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

  atleta = db.relationship("Atleta", backref=db.backref("campanhas", lazy=True))

  doacoes_campanha = db.relationship("DoacaoCampanha", backref="campanha", lazy=True)


  def __init__(self, titulo, descricao, numero_time, meta_arrecadacao, valor_arrecadado, conta_destino, atleta_id):
    self.titulo = titulo
    self.descricao = descricao
    self.numero_time = numero_time
    self.meta_arrecadacao = meta_arrecadacao
    self.valor_arrecadado = valor_arrecadado
    self.conta_destino = conta_destino
    self.atleta_id = atleta_id

  def __repr__(self):
    return f'<Campanha {self.id}>'