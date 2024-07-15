from flask_restful import Resource, reqparse, marshal, request
from helpers.auth.token_handler.token_verificador import token_verifica
from model.atleta import *
from model.message import *
from helpers.database import db
from helpers.base_logger import logger
import re
from password_strength import PasswordPolicy
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from model.campanha import *
from sqlalchemy import desc

parser = reqparse.RequestParser()
parser.add_argument('nome', type=str, help='Problema no nome', required=True)
parser.add_argument('genero', type=str, help='Problema no genero', required=True)
parser.add_argument('nascimento', type=str, help='Problema no nascimento', required=True)
parser.add_argument('telefone', type=str, help='Problema no telefone', required=True)
parser.add_argument('email', type=str, help='Problema no email', required=True)
parser.add_argument('senha', type=str, help='Problema na senha', required=True)

padrao_email = r'^[\w\.-]+@[\w\.-]+\.\w+$'

padrao_senha = PasswordPolicy.from_names(
    length=8,
    uppercase=1,
    numbers=1,
    special=1
)

class Atletas(Resource):
    def get(self):
        logger.info("Atletas listadas com sucesso!")
        atletas = Atleta.query.all()
        return marshal(atletas, atleta_fields), 200

    def post(self):
        args = parser.parse_args()
        try:
            nome = args["nome"]
            genero = args["genero"]
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

            atleta = Atleta(nome, genero, nascimento, telefone, email, senha)

            db.session.add(atleta)
            db.session.commit()

            logger.info("Atleta cadastrada com sucesso!")
            return marshal(atleta, atleta_fields), 201

        except IntegrityError as e:
            if 'email' in str(e.orig):
                message = Message("Email já existe!", 2)
                return marshal(message, message_fields), 400

            elif 'telefone' in str(e.orig):
                message = Message("Telefone já existe!", 2)
                return marshal(message, message_fields), 400

        except Exception as e:
            logger.error(f"error: {e}")
            message = Message("Erro ao cadastrar atleta", 2)
            return marshal(message, message_fields), 404

class AtletaCampaigns(Resource):
    @token_verifica
    def get(self, tipo, refresh_token, id_campanha):
        if tipo != 'atleta':
            message = Message("Acesso Não autorizado", 2)
            return marshal(message, message_fields), 401
        pageIndex = request.args.get("pageIndex", 1, type=int)
        perPage= request.args.get("per-page", 6, type=int)

        atleta = Atleta.query.get(id_campanha)

        campanhas_query = Campanha.query.order_by(desc(Campanha.created_at))
        campanha = campanhas_query.filter_by(atleta_id=atleta.id_pessoa).paginate(page=pageIndex, per_page=perPage, error_out=False)

        data = {"campanhas": campanha.items, "indiceDaPagina": pageIndex, "itemsPorPagina": perPage, "totalCampanhas": len(campanha.items)}

        logger.info("Atletas listadas com sucesso!")
        return marshal(data, campanhasFieldsPagination), 200

class CampanhaAtletaById(Resource):
    @token_verifica
    def get(self, tipo, refreshToken, usuario_id, id):
        if tipo != 'atleta':
            logger.error(f"Usuário não autorizado")
            message = Message("Acesso Não autorizado", 2)
            return marshal(message, message_fields), 401
        
        campanha = Campanha.query.filter_by(id=id, atleta_id=usuario_id).first()

        if campanha is None:
            logger.error(f"Campanha {id} não encontrado")
            message = Message(f"Campanha {id} não encontrado", 1)
            return marshal(message, message_fields), 404

        logger.info(f"Campanha {id} encontrado com sucesso")
        return marshal(campanha, campanha_fields), 200

class AtletaById(Resource):
    def get(self, id):
        atleta = Atleta.query.get(id)

        if atleta is None:
            logger.error(f"Atleta {id} não encontrado")
            message = Message(f"Atleta {id} não encontrado", 1)
            return marshal(message, message_fields), 404

        logger.info(f"Atleta {id} encontrado com sucesso!")
        return marshal(atleta, atleta_fields)

   # @token_verifica
    def put(self, id):
    #    if tipo != 'atleta':
     #       logger.error(f'Usuário não autorizado')
      #      message = Message("Acesso não autorizado", 2)
       #     return marshal(message, message_fields), 401

        args = parser.parse_args()

        try:
            atleta = Atleta.query.get(id)

            if atleta is None:
                logger.error(f"Atleta {id} não encontrado")
                message = Message(f"Atleta {id} não encontrado", 1)
                return marshal(message, message_fields), 404

            atleta.nome = args["nome"]
            atleta.genero = args["genero"]
            atleta.nascimento = args["nascimento"]
            atleta.telefone = args["telefone"]
            atleta.email = args["email"]
            senha = args["senha"]

            # Validações dos campos
            if not atleta.nome or len(atleta.nome) < 3:
                logger.info("Nome não informado ou não tem no mínimo 3 caracteres")
                message = Message("Nome não informado ou não tem no mínimo 3 caracteres", 2)
                return marshal(message, message_fields), 400

            if not atleta.nascimento:
                logger.info("Nascimento não informado")
                message = Message("Nascimento não informado", 2)
                return marshal(message, message_fields), 400

            if not re.match(r'^\d{2}/\d{2}/\d{4}$', atleta.nascimento):
                logger.info("Formato de data de nascimento inválido. Use o formato dd/mm/yyyy.")
                message = Message("Formato de data de nascimento inválido. Use o formato dd/mm/yyyy.", 2)
                return marshal(message, message_fields), 400

            try:
                data_nascimento = datetime.strptime(atleta.nascimento, "%d/%m/%Y")
            except ValueError:
                logger.info("Data de nascimento inválida.")
                message = Message("Data de nascimento inválida.", 2)
                return marshal(message, message_fields), 400

            data_minima = datetime.now() - timedelta(days=16*365.25)

            if data_nascimento > data_minima:
                logger.info("Você deve ter pelo menos 16 anos para se cadastrar.")
                message = Message("Você deve ter pelo menos 16 anos para se cadastrar.", 2)
                return marshal(message, message_fields), 400

            if not atleta.telefone:
                logger.info("Telefone não informado")
                message = Message("Telefone não informado", 2)
                return marshal(message, message_fields), 400

            if not re.match(r'^\(\d{2}\) \d{5}-\d{4}$', atleta.telefone):
                logger.info("Telefone informado incorretamente")
                message = Message("Telefone informado incorretamente", 2)
                return marshal(message, message_fields), 400

            if not atleta.email:
                logger.info("Email não informado")
                message = Message("Email não informado", 2)
                return marshal(message, message_fields), 400

            padrao_email = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            if re.match(padrao_email, atleta.email) is None:
                logger.info("Email informado incorretamente")
                message = Message("Email informado incorretamente", 2)
                return marshal(message, message_fields), 400

            if not senha:
                logger.info("Senha não informada")
                message = Message("Senha não informada", 2)
                return marshal(message, message_fields), 400

            padrao_senha = PasswordPolicy.from_names(length=8, uppercase=1, numbers=1, special=1)
            verify_senha = padrao_senha.test(senha)
            if len(verify_senha) != 0:
                message = Message("Senha informada incorretamente", 2)
                return marshal(message, message_fields), 400

            atleta.senha = generate_password_hash(senha)  # Hashing the password before saving

            db.session.add(atleta)
            db.session.commit()

            logger.info("Atleta atualizado com sucesso!")
            return marshal(atleta, atleta_fields), 200

        except Exception as e:
            logger.error(f"Error: {e}")
            message = Message("Erro ao atualizar atleta", 2)
            return marshal(message, message_fields), 404

    def delete(self, id):
        atleta = Atleta.query.get(id)

        if atleta is None:
            logger.error(f"Atleta {id} não encontrado")
            message = Message(f"Atleta {id} não encontrado", 1)
            return marshal(message, message_fields), 404

        db.session.delete(atleta)
        db.session.commit()

        message = Message("Atleta deletado com sucesso!", 3)
        return marshal(message, message_fields), 200

class AtletaByNome(Resource):
    def get(self, nome):
        atleta = Atleta.query.filter_by(nome=nome).all()

        if atleta is None:
            logger.error(f"Atleta {id} não encontrado")

            message = Message(f"Atleta {id} não encontrado", 1)
            return marshal(message), 404

        logger.info(f"Atleta {id} encontrado com sucesso!")
        return marshal(atleta, atleta_fields), 200

class AtletaMe(Resource):
    def get(self):
        atleta = Atleta.query.get()

        if atleta is None:
            logger.error(f"Atleta {id} não encontrada")

            message = Message(f"Atleta {id} não encontrada", 1)
            return marshal(message), 404

        logger.info(f"Atleta {id} encontrada com sucesso!")
        return marshal(atleta, atleta_fields), 200
class AtletaInfo(Resource):
    @token_verifica
    def get(self, tipo, refreshToken, usuario_id):
        if tipo != 'atleta':
            message = Message("Acesso Não autorizado", 2)
            return marshal(message, message_fields), 401
        atleta = Atleta.query.get(usuario_id)
        return marshal(atleta, atleta_fields), 200
    