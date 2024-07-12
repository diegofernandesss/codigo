from flask_restful import fields
from helpers.database import db
from model.pessoa import Pessoa

doador_fields = {
  'id': fields.Integer,
  'nome': fields.String,
  'nascimento': fields.String,
  'telefone': fields.String,
  'email': fields.String,
  'senha': fields.String,
}

doadorCompleto_fields = {
  'id': fields.Integer,
  'nome': fields.String,
  'nascimento': fields.String,
  'telefone': fields.String,
  'email': fields.String,
  'cpf': fields.String,
  'numConta': fields.String,
}

class Doador(Pessoa):
    __tablename__ = "doador"

    id_pessoa = db.Column(db.Integer, db.ForeignKey("pessoa.id"), primary_key=True)
    cpf = db.Column(db.String, nullable=True)
    numConta = db.Column(db.String, nullable=True)

    # id_doacao = db.relationship("Doacao", backref=db.backref("doacao", lazy=True))

    __mapper_args__ = {"polymorphic_identity": "doador"}

    def __init__(self, nome, nascimento, telefone, email, senha):
      super().__init__(nome, nascimento, telefone, email, senha)


    def __repr__(self):
      return f'<Doador {self.nome}>'
