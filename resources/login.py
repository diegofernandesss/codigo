from flask_restful import Resource, reqparse, marshal
from helpers.auth.token_handler.token_singleton import token_criador
from model.pessoa import *
from model.message import *
from model.login import *
from helpers.base_logger import logger

parser = reqparse.RequestParser()
parser.add_argument('email', type=str, help='Problema no email.', required=True)
parser.add_argument('senha', type=str, help='Problema na senha.', required=True)

class Login(Resource):
    def post(self):
        args = parser.parse_args()
        pessoa = Pessoa.query.filter_by(email=args["email"]).first()
        if pessoa is None:
            logger.error(f"A pessoa do email:  {args['email']} não foi encontrado")

            message = Message(f"Email ou senha inválidos.", 1)
            return marshal(message, message_fields), 404

        if not pessoa.verificar_senha(args['senha']):
            message = Message("Email ou senha inválidos.", 1)
            return marshal(message, message_fields), 404


        token = token_criador.create(pessoa.tipo, pessoa.id)
        login = LoginModel(token, pessoa.tipo)
        return marshal(login, login_fields), 200
