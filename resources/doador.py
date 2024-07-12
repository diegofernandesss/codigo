from flask_restful import Resource, reqparse, marshal
from model.doador import *
from model.message import *
from helpers.database import db
from helpers.base_logger import logger
import re
from validate_docbr import CPF
from password_strength import PasswordPolicy
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from helpers.auth.token_handler.token_verificador import token_verifica
from werkzeug.security import generate_password_hash, check_password_hash


parser = reqparse.RequestParser()
parser.add_argument('nome', type=str, help='Problema no nome', required=False)
parser.add_argument('nascimento', type=str, help='Problema no nascimento', required=False)
parser.add_argument('telefone', type=str, help='Problema no telefone', required=False)
parser.add_argument('email', type=str, help='Problema no email', required=False)
parser.add_argument('senha', type=str, help='Problema na senha', required=False)
parser.add_argument('cpf', type=str, help='Problema no cpf', required=False)
parser.add_argument('numConta', type=str, help='Problema no número da conta', required=False)
parser.add_argument('agenciaConta', type=str, help='Problema na agência da conta', required=False)

padrao_email = r'^[\w\.-]+@[\w\.-]+\.\w+$'

cpfValidate = CPF()

padrao_senha = PasswordPolicy.from_names(
    length=8,
    uppercase=1,
    numbers=1,
    special=1
)

class Doadores(Resource):
    def get(self):
        logger.info("Doadores listados com sucesso!")
        doadores = Doador.query.all()
        return marshal(doadores, doador_fields), 200

    def post(self):
        args = parser.parse_args()

        try:
            nome = args["nome"]
            nascimento = args["nascimento"]
            telefone = args["telefone"]
            email = args["email"]
            senha = args["senha"]

            if not nome:
                logger.info("Nome não informado")
                message = Message("Nome não informado", 2)
                return marshal(message, message_fields), 400

            if not nome or len(nome) < 3:
                logger.info("Nome não informado ou não tem no mínimo 3 caracteres")
                message = Message("Nome não informado ou não tem no mínimo 3 caracteres", 2)
                return marshal(message, message_fields), 400

            if not nascimento:
                logger.info("Nascimento não informado")
                message = Message("Nascimento não informado", 2)
                return marshal(message, message_fields), 400

            if not re.match(r'^\d{2}/\d{2}/\d{4}$', nascimento):
                logger.info("Formato de data de nascimento inválido. Use o formato dd/mm/yyyy.")
                message = Message("Formato de data de nascimento inválido. Use o formato dd/mm/yyyy.", 2)
                return marshal(message, message_fields), 400

            try:
                data_nascimento = datetime.strptime(nascimento, "%d/%m/%Y")
            except ValueError:
                logger.info("Data de nascimento inválida.")
                message = Message("Data de nascimento inválida.", 2)
                return marshal(message, message_fields), 400

            data_minima = datetime.now() - timedelta(days=16*365.25)

            if data_nascimento > data_minima:
                logger.info("Você deve ter pelo menos 16 anos para se cadastrar.")
                message = Message("Você deve ter pelo menos 16 anos para se cadastrar.", 2)
                return marshal(message, message_fields), 400

            if not telefone:
                logger.info("Telefone não informado")
                message = Message("Telefone não informado", 2)
                return marshal(message, message_fields), 400

            if not re.match(r'^\(\d{2}\) \d{5}-\d{4}$', telefone):
                logger.info("Telefone informado incorretamente")
                message = Message("Telefone informado incorretamente", 2)
                return marshal(message, message_fields), 400

            if not email:
                logger.info("Email não informado")
                message = Message("Email não informado", 2)
                return marshal(message, message_fields), 400

            if re.match(padrao_email, email) is None:
                logger.info("Email informado incorretamente")
                message = Message("Email informado incorretamente", 2)
                return marshal(message, message_fields), 400

            if not senha:
                logger.info("Senha não informada")
                message = Message("Senha não informada", 2)
                return marshal(message, message_fields), 400

            verify_senha = padrao_senha.test(senha)
            if len(verify_senha) != 0:
                message = Message("Senha informada incorretamente", 2)
                return marshal(message, message_fields), 400

            doador = Doador(nome, nascimento, telefone, email, senha)

            db.session.add(doador)
            db.session.commit()

            logger.info("Doador cadastrado com sucesso!")
            return marshal(doador, doador_fields), 201

        except IntegrityError as e:

            if 'email' in str(e.orig):
                message = Message("Email já existe!", 2)
                return marshal(message, message_fields), 409

            if 'telefone' in str(e.orig):
                message = Message("Telefone já existe!", 2)
                return marshal(message, message_fields), 409

        except Exception as e:
            logger.error(f"Error: {e}")
            message = Message("Erro ao cadastrar o doador", 2)
            return marshal(message, message_fields), 404

class DoadorById(Resource):
    @token_verifica
    def get(self, tipo, refresh_token, id_usuario, id_campanha):
        if tipo != 'doador':
            message = Message("Acesso não autorizado", 1)
            return  marshal(message, message_fields)

        campanha = Campanha.query.get(id_campanha)

        if campanha is None:
            logger.error(f"Campanha {id_campanha} não encontrada")
            message = Message(f"Campanha {id_campanha} não encontrada", 1)
            return marshal(message, message_fields), 404

        logger.info(f"Campanha {id_campanha} encontrada com sucesso!")
        return marshal(campanha, campanha_fields), 200


class DoadorById(Resource):
    @token_verifica
    def get(self, tipo, refreshToken, usuario_id, id):
        if tipo != "doador":
            logger.error(f"Usuário {id_usuario} não é doador")
            message = Message("Acesso Não autorizado", 2)
            return marshal(message, message_fields), 401

        doador = Doador.query.get(id)

        if doador is None:
            logger.error(f"Doador {id} não encontrado")
            message = Message(f"Doador {id} não encontrado", 1)
            return marshal(message, message_fields), 404
        logger.info(f"Doador {id} encontrado com sucesso!")
        return marshal(doador, doador_fields), 200

    @token_verifica
    def put(self, tipo, refreshToken, usuario_id, id):
        if tipo != "doador":
            logger.error(f"Usuario nao autorizado")
            message = Message("Acesso Não autorizado", 2)
            return marshal(message, message_fields), 401

        args = parser.parse_args()
        try:
            doador = Doador.query.get(id)

            if doador is None:
                logger.error(f"Doador {id} não encontrado")
                message = Message(f"Doador {id} não encontrado", 1)
                return marshal(message, message_fields), 404

            nome = args["nome"]
            nascimento = args["nascimento"]
            telefone = args["telefone"]
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

            if not re.match(r'^\d{2}/\d{2}/\d{4}$', nascimento):
                logger.info("Formato de data de nascimento inválido. Use o formato dd/mm/yyyy.")
                message = Message("Formato de data de nascimento inválido. Use o formato dd/mm/yyyy.", 2)
                return marshal(message, message_fields), 400

            try:
                data_nascimento = datetime.strptime(nascimento, "%d/%m/%Y")
            except ValueError:
                logger.info("Data de nascimento inválida.")
                message = Message("Data de nascimento inválida.", 2)
                return marshal(message, message_fields), 400

            data_minima = datetime.now() - timedelta(days=16*365.25)

            if data_nascimento > data_minima:
                logger.info("Você deve ter pelo menos 16 anos para se cadastrar.")
                message = Message("Você deve ter pelo menos 16 anos para se cadastrar.", 2)
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

            if not re.match(r'^\(\d{2}\) \d{5}-\d{4}$', telefone):
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
            
            doador.nome = nome
            doador.nascimento = nascimento
            doador.telefone = telefone
            doador.email = email
            doador.senha = generate_password_hash(senha)

            db.session.add(doador)
            db.session.commit()

            logger.info("Doador atualizado com sucesso!")
            return marshal(doador, doador_fields), 200

        except IntegrityError as e:
            if 'email' in str(e.orig):
                message = Message("email já existe!", 2)
                return marshal(message, message_fields), 409
        except Exception as e:
            logger.error(f"Error: {e}")
            message = Message("Erro ao atualizar o doador", 2)
            return marshal(message, message_fields), 404

    def delete(self, id):
        doador = Doador.query.get(id)

        if doador is None:
            logger.error(f"Doador {id} não encontrado")
            message = Message(f"Doador {id} não encontrado", 2)
            return marshal(message, message_fields), 404

        db.session.delete(doador)
        db.session.commit()

        message = Message("Doador deletado com sucesso!", 3)
        return marshal(message, message_fields), 200

class DoadorByNome(Resource):
    def get(self, query):
        try:
            doadores = Doador.query.filter(
                or_(
                    Doador.telefone == query,
                )
            ).all()
        except ValueError:
            doadores = Doador.query.filter(
                or_(
                    Doador.nome.ilike(f"%{query}%"),
                    Doador.email.ilike(f"%{query}%"),
                )
            ).all()

        if not doadores:
            logger.error(f"Doador {query} não encontrado")
            message = Message(f"Doador {query} não encontrado", 1)
            return marshal(message, message_fields), 404

        logger.info(f"Doador {query} encontrado com sucesso!")
        return marshal(doadores, doador_fields), 200

class updatedInfoPaymentDoador(Resource):
    @token_verifica
    def put(self, tipo, refresh_token, id_usuario):
        if tipo != "doador":
            logger.error(f"Usuário {id_usuario} não é doador")
            message = Message("Acesso Não autorizado", 2)
            return marshal(message, message_fields), 401

        args = parser.parse_args()
        try:
            doador = Doador.query.get(id_usuario)

            cpf = args["cpf"]
            numConta = args["numConta"]

            if not cpf:
                logger.info("CPF não informado")
                message = Message("CPF não informado", 2)
                return marshal(message, message_fields), 400

            if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', cpf):
                message = Message("cpf no formato errado", 2)
                return marshal(message, message_fields), 400

            if not cpfValidate.validate(args["cpf"]):
                logger.error(f"CPF {args['cpf']} não valido")
                message = Message("cpf Inválido", 2)
                return marshal(message, message_fields), 400

            if not numConta:
                logger.info("Número da conta não informado")
                message = Message("Número da conta não informado", 2)
                return marshal(message, message_fields), 400

            if not numConta or len(numConta) < 5 or len(numConta) > 5:
                logger.info("Número da conta tem que ser 5 números")
                message = Message("Número da conta tem que ser 5 números", 2)
                return marshal(message, message_fields), 400

            doador.cpf = cpf
            doador.numConta = numConta

            db.session.add(doador)
            db.session.commit()

            logger.info("Conta do doador atualizada com sucesso!")
            return marshal(doador, doadorCompleto_fields), 200
        except IntegrityError as e:
            if 'cpf' in str(e.orig):
                message = Message("cpf já existe!", 2)
                return marshal(message, message_fields), 409
        except Exception as e:
            logger.error(f"Error: {e}")
            message = Message("Erro ao atualizar a conta do doador", 2)
            return marshal(message, message_fields), 404
        

class DoadorInfo(Resource):
    @token_verifica
    def get(self, tipo, refreshToken, usuario_id):
        if tipo != 'doador':
            message = Message("Acesso Não autorizado", 2)
            return marshal(message, message_fields), 401
        doadores = Doador.query.get(usuario_id)
        return marshal(doadores, doadorCompleto_fields), 200
