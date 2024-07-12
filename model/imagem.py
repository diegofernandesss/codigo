from flask_restful import fields
from helpers.database import db

imagem_fields = {
    'id': fields.Integer,
    'file': fields.LargeBinary,
}

class Imagem(db.Model):
    __tablename__ = 'imagem'

    id = db.Column(db.Integer, primary_key=True)
    file = db.Column(db.LargeBinary, nullable=False)

    def __init__ (self, file):
        self.file = file

    def __repr__(self):
        return '<Imagem {self.id}>'
