from flask_restful import fields
from helpers.database import db
from datetime import datetime

pagamento_fields = {
  'id': fields.Integer,
  'nome': fields.String,
  'email': fields.String,
  'valor': fields.Float,
  'time': fields.DateTime,
}

class Pagamento(db.Model):
    __tablename__ = "pagamento"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    cpf = db.Column(db.String, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


    def __init__(self, nome, email, cpf, valor):
        self.nome = nome
        self.email = email
        self.cpf = cpf
        self.valor = valor

    def __repr__(self):
        return f"Pagamento{self.id}"
