from flask_restful import Resource, reqparse, marshal
from model.pessoa import *
from model.message import *
from helpers.base_logger import logger
import re
from password_strength import PasswordPolicy

parser = reqparse.RequestParser()
parser.add_argument('nome', type=str, help='Problema no nome', required=True)
parser.add_argument('nascimento', type=str, help='Problema no nascimento', required=True)
parser.add_argument('telefone', type=str, help='Problema no telefone', required=True)
parser.add_argument('endereco', type=str, help='Problema no endereco', required=True)
parser.add_argument('email', type=str, help='Problema no email', required=True)
parser.add_argument('senha', type=str, help='Problema na senha', required=True)

padrao_email = r'^[\w\.-]+@[\w\.-]+\.\w+$'

padrao_senha = PasswordPolicy.from_names(
    length=8,
    uppercase=1,
    numbers=1,
    special=1
)

class Pessoas(Resource):
    def get(self):
        logger.info("Pessoas listadas com sucesso!")
        pessoas = Pessoa.query.all()
        return marshal(pessoas, pessoa_fields), 200

    def post(self):
        args = parser.parse_args()

        try:
            nome = args["nome"]
            nascimento = args["nascimento"]
            telefone = args["telefone"]
            endereco = args["endereco"]
            email = args["email"]
            senha = args["senha"]

            if not nome or len(nome) < 3:
                logger.info("Nome não informado ou não tem no mínimo 3 caracteres")
                message = Message("Nome não informado ou não tem no mínimo 3 caracteres", 2)
                return marshal(message, message_fields), 400

            if not nascimento:
                logger.info("Nascimento não informado")
                message = Message("Nascimento não informado", 2)
                return marshal(message, message_fields), 400

            if not telefone:
                logger.info("Telefone não informado")
                message = Message("Telefone não informado", 2)
                return marshal(message, message_fields), 400

            if not email:
                logger.info("Email não informado")
                message = Message("Email não informado", 2)
                return marshal(message, message_fields), 400

            if re.match(padrao_email, email) is None:
                logger.info("Email informado incorretamente")
                message = Message("Email informado incorretamente", 2)
                return marshal(message, message_fields), 400

            if not re.match(r'^\d{11}$', telefone):
                logger.info("Telefone informado incorretamente")
                message = Message("Telefone informado incorretamente", 2)
                return marshal(message, message_fields), 400

            if not senha:
                logger.info("Senha não informada")
                message = Message("Senha não informada", 2)
                return marshal(message, message_fields), 400

            verify_senha = padrao_senha.test(senha)
            if len(verify_senha) != 0:
                message = Message("Senha informada incorretamente", 2)
                return marshal(message, message_fields), 400

            pessoa = Pessoa(nome, nascimento, telefone, endereco, email, senha)

            db.session.add(pessoa)
            db.session.commit()

            logger.info("Pessoa cadastrada com sucesso!")
            return marshal(pessoa, pessoa_fields), 201
        except IntegrityError as e:
            if 'email' in str(e.orig):
                message = Message("Email já existe!", 2)
                return marshal(message, message_fields), 409
        except Exception as e:
            logger.error(f"Error: {e}")
            message = Message("Erro ao cadastrar pessoa", 2)
            return marshal(message, message_fields), 404

class PessoaById(Resource):
    def get(self, id):
        pessoa = Pessoa.query.get(id)

        if pessoa is None:
            logger.error(f"Pessoa {id} não encontrada")
            message = Message(f"Pessoa {id} não encontrada", 1)
            return marshal(message, message_fields), 404

        logger.info(f"Pessoa {id} encontrada com sucesso!")
        return marshal(pessoa, pessoa_fields), 200

    def put(self, id):
        args = parser.parse_args()

        try:
            pessoa = Pessoa.query.get(id)
            if pessoa is None:
                logger.error(f"Pessoa {id} não encontrada")
                message = Message(f"Pessoa {id} não encontrada", 1)
                return marshal(message, message_fields), 404

            nome = args["nome"]
            nascimento = args["nascimento"]
            telefone = args["telefone"]
            endereco = args["endereco"]
            email = args["email"]
            senha = args["senha"]

            if not nome or len(nome) < 3:
                logger.info("Nome não informado ou não tem no mínimo 3 caracteres")
                message = Message("Nome não informado ou não tem no mínimo 3 caracteres", 2)
                return marshal(message, message_fields), 400

            if not nascimento:
                logger.info("Nascimento não informado")
                message = Message("Nascimento não informado", 2)
                return marshal(message, message_fields), 400

            if not telefone:
                logger.info("Telefone não informado")
                message = Message("Telefone não informado", 2)
                return marshal(message, message_fields), 400

            if not email:
                logger.info("Email não informado")
                message = Message("Email não informado", 2)
                return marshal(message, message_fields), 400

            if re.match(padrao_email, email) is None:
                logger.info("Email informado incorretamente")
                message = Message("Email informado incorretamente", 2)
                return marshal(message, message_fields), 400

            if not re.match(r'^\d{11}$', telefone):
                logger.info("Telefone informado incorretamente")
                message = Message("Telefone informado incorretamente", 2)
                return marshal(message, message_fields), 400

            if not senha:
                logger.info("Senha não informada")
                message = Message("Senha não informada", 2)
                return marshal(message, message_fields), 400

            verify_senha = padrao_senha.test(senha)
            if len(verify_senha) != 0:
                message = Message("Senha informada incorretamente", 2)
                return marshal(message, message_fields), 400

            pessoa.nome = nome
            pessoa.nascimento = nascimento
            pessoa.telefone = telefone
            pessoa.endereco = endereco
            pessoa.email = email
            pessoa.senha = senha

            db.session.add(pessoa)
            db.session.commit()

            logger.info("Pessoa atualizada com sucesso!")
            return marshal(pessoa, pessoa_fields), 200
        except Exception as e:
            logger.error(f"Error: {e}")
            message = Message("Erro ao atualizar pessoa", 2)
            return marshal(message, message_fields), 404

    def delete(self, id):
        pessoa = Pessoa.query.get(id)

        if pessoa is None:
            logger.error(f"Pessoa {id} não encontrada")
            message = Message(f"Pessoa {id} não encontrada", 1)
            return marshal(message, message_fields), 404

        db.session.delete(pessoa)
        db.session.commit()

        message = Message("Pessoa deletada com sucesso!", 3)
        return marshal(message, message_fields), 200

class PessoaByNome(Resource):
    def get(self, nome):
        pessoa = Pessoa.query.filter_by(nome=nome).all()

        if not pessoa:
            logger.error(f"Pessoa {nome} não encontrada")
            message = Message(f"Pessoa {nome} não encontrada", 1)
            return marshal(message, message_fields), 404

        logger.info(f"Pessoa {nome} encontrada com sucesso!")
        return marshal(pessoa, pessoa_fields), 200

class PessoaMe(Resource):
    def get(self):
        pessoa = Pessoa.query.get()

        if pessoa is None:
            logger.error(f"Pessoa não encontrada")
            message = Message("Pessoa não encontrada", 1)
            return marshal(message, message_fields), 404

        logger.info("Pessoa encontrada com sucesso!")
        return marshal(pessoa, pessoa_fields), 200
