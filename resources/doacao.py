from flask_restful import Resource, reqparse, marshal
from model.message import *
from helpers.base_logger import logger
from helpers.database import db
from datetime import datetime
import re
from helpers.auth.token_handler.token_verificador import token_verifica
from validate_docbr import CPF
from model.campanha import Campanha
from model.doador import Doador
from model.atleta import Atleta
from model.doacaoCampanha import DoacaoCampanha, doacaoCampanha_fields, historico_doacoes_fields
from flask_mail import Message as MailMessage, Mail

parser = reqparse.RequestParser()

parser.add_argument("valor", type=float, required=True, help="Valor não informado")
parser.add_argument('campanha_id', type=str, required=True, help='Id da campanha não informado')

padrao_email = r'^[\w\.-]+@[\w\.-]+\.\w+$'

cpf = CPF()
mail = Mail()

"056.998.308-80"
"290.297.910-04"
"607.298.816-44"
"167.167.991-17"
"677.986.197-98"

class DoacoesCampanha(Resource):
    @token_verifica
    def get(self, tipo, refreshToken, id_usuario):
        if tipo != "doador":
            logger.error(f"Usuário {id_usuario} não é doador")
            message = Message("Usuário não autorizado", 2)
            return marshal(message, message_fields), 401

        doacoes = DoacaoCampanha.query.all()
        logger.info('Listagem de doações de campanha com sucesso!')
        return marshal(doacoes, doacaoCampanha_fields), 200

    @token_verifica
    def post(self, tipo, refresh_token, id_usuario):
        if tipo != "doador":
            logger.error(f"Usuário {id_usuario} não é doador")
            message = Message("Acesso não autorizado", 2)
            return marshal(message, message_fields), 401

        args = parser.parse_args()
        try:
            valor = args["valor"]
            campanhaId = args["campanha_id"]

            doador = Doador.query.get(id_usuario)
            campanha = Campanha.query.get(campanhaId)

            if campanha.meta_arrecadacao == 0:
                logger.info("Campanha já atingiu a meta de arrecadação")
                message = Message("Campanha já atingiu a meta de arrecadação", 2)
                return marshal(message, message_fields), 400
            
            if valor > campanha.meta_arrecadacao:
                logger.info("Valor maior que a meta de arrecadação")
                message = Message("Valor maior que a meta de arrecadação", 2)
                return marshal(message, message_fields), 400
                        
            if valor <= 0:
                logger.info("Valor da doação invalido")
                message = Message("Valor da doação inválida", 2)
                return marshal(message, message_fields), 400

            if campanha is None:
                logger.info("Campanha não encontrada")
                message = Message("Campanha não encontrada", 2)
                return marshal(message, message_fields), 404

            if doador.cpf is None:
                logger.info("Doador não fez o cadastro do cpf")
                message = Message("Doador não fez o cadastro do CPF", 2)
                return marshal(message, message_fields), 400

            if doador.numConta is None or len(doador.numConta) != 5 :
                logger.info("Doador não fez o cadastro do número da conta ou não tem 5 caracteres")
                message = Message("Doador não fez o cadastro do número da conta ou não tem 5 caracteres", 2)
                return marshal(message, message_fields), 400

            doacao = DoacaoCampanha(valor, campanhaId, doador.nome, doador.email, doador.cpf, doador.numConta, doador.id_pessoa)
            atleta = Atleta.query.filter_by(id=campanha.atleta_id).first()

            campanha.valor_arrecadado += valor
            campanha.meta_arrecadacao -= valor
            if campanha.meta_arrecadacao == 0:
                campanha.status = "Finalizada"
            db.session.add(doacao)
            db.session.add(campanha)
            db.session.commit()

            msg = MailMessage("Confirmação de doação", sender="atheleteaid@gmail.com", recipients=[doador.email])

            msg.body = f'''
                Envio de email com a Confirmação de doação para a campanha: {campanha.titulo}
                '''
            msg.html = f'''
                <html>
                    <body>
                        <center>
                            <h1>Confirmação de doação</h1>
                            <p>Envio de email com a Confirmação de doação da campanha: {campanha.titulo}</p>
                            <p> Olá, {doador.nome} ! Ficamos muito feliz com a sua doação !</p>
                            <p> O Atleta {atleta.nome}, fica bastante grato por sua doação.</p>
                            <p>Segue o comprovante: </p>
                        </center>

                        <div class="container">
                <h1>Comprovante de Transferência</h1>

                <div class="section">
                    <div class="section-header">Dados do Doador</div>
                    <p class="info"><strong>Nome do Doador:</strong> {doador.nome}</p>
                    <p class="info"><strong>Valor:</strong> R$ {valor:.2f}</p>
                    <p class="info"><strong>Conta de Origem:</strong> {doador.numConta}</p>
                </div>

                <div class="section">
                    <div class="section-header">Dados do Atleta</div>
                    <p class="info"><strong>Nome do Atleta:</strong> {atleta.nome}</p>
                    <p class="info"><strong>Conta de Destino:</strong> {campanha.conta_destino}</p>
                    <p class="info"><strong>Motivo da Doação:</strong> {campanha.titulo}</p>
                </div>

                <p>Obrigado por sua generosidade!</p>
            </div>

            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: auto;
                    background: #fff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
                h1, h2, p {{
                    margin: 0 0 10px;
                }}
                .section {{
                    margin-bottom: 20px;
                }}
                .section-header {{
                    font-size: 18px;
                    font-weight: bold;
                    border-bottom: 2px solid #eee;
                    margin-bottom: 10px;
                    padding-bottom: 5px;
                }}
                .info {{
                    margin-bottom: 5px;
                }}
                .info strong {{
                    display: inline-block;
                    width: 150px;
                }}
            </style>
                    </body>
                </html>
                '''
            # mail.send(msg)

            logger.info("Doacao cadastrado com sucesso!")
            return marshal(doacao, doacaoCampanha_fields), 201
        except:
            logger.error("Erro ao cadastrar doacao")
            message = Message("Erro ao cadastrar doação", 2)
            return marshal(message, message_fields), 404

class DoacoesDoador(Resource):
    @token_verifica
    def get(self, tipo, refreshToken, usuario_id):
        if tipo != 'doador':
            logger.error(f"Usuário não autorizado")
            message = Message("Acesso Não autorizado", 2)
            return marshal(message, message_fields), 401

        doacoes = DoacaoCampanha.query.filter_by(doador_id = usuario_id).all()

        if not doacoes:
            logger.error(f"Não há doações para o doador {usuario_id}")
            message = Message(f"Não há doações para o doador {usuario_id}", 1)
            return marshal(message, message_fields), 404

        logger.info(f"Doações do doador {usuario_id} encontradas com sucesso!")
        return marshal(doacoes, doacaoCampanha_fields), 200

class HistoricoDoacoesAtleta(Resource):
    @token_verifica
    def get(self, tipo, refreshToken, usuario_id):
        if tipo != "atleta":
            logger.error(f"Usuario nao autorizado")
            message = Message("Acesso Não autorizado", 2)
            return marshal(message, message_fields), 401

        # Consulta as campanhas criadas pelo atleta
        campanhas = Campanha.query.filter_by(atleta_id=usuario_id).all()

        if not campanhas:
            logger.error(f"Não há campanhas para o atleta {usuario_id}")
            message = Message(f"Não há campanhas para o atleta {usuario_id}", 1)
            return marshal(message, message_fields), 404

        resultado = []
        for campanha in campanhas:
            doacoes = DoacaoCampanha.query.filter_by(campanha_id=campanha.id).all()
            for doacao in doacoes:
                doador = Doador.query.get(doacao.doador_id)
                # if doador:
                resultado.append({
                    'campanha_id': campanha.id,
                    'campanha_titulo': campanha.titulo,
                    'doador_id': doacao.doador_id,
                    'doador_nome': doacao.nome,
                    'valor': doacao.valor
                })


        logger.info(f"Histórico de doações para o atleta {usuario_id} encontrado com sucesso!")
        return marshal(resultado, historico_doacoes_fields), 200
