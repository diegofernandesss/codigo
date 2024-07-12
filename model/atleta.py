from flask_restful import fields
from helpers.database import db
from model.pessoa import Pessoa

atleta_fields = {
  'id': fields.Integer,
  'nome': fields.String,
  'genero': fields.String,
  'nascimento': fields.String,
  'telefone': fields.String,
  'email': fields.String,
  'senha' : fields.String,
}

class Atleta(Pessoa):
    __tablename__ = "atleta"

    id_pessoa = db.Column(db.Integer, db.ForeignKey("pessoa.id"), primary_key=True)
    genero = db.Column(db.String, nullable=False)


    __mapper_args__ = { "polymorphic_identity": "atleta",}

    def __init__(self, nome, genero, nascimento, telefone, email, senha):
      super().__init__(nome, nascimento, telefone, email, senha)
      self.genero = genero

    def __repr__(self):
      return f'<Atleta {self.nome}>'

