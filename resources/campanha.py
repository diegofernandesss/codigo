from flask_restful import Resource, reqparse, marshal, request
from model.campanha import *
from model.message import *
from helpers.base_logger import logger
from sqlalchemy import desc
from helpers.auth.token_handler.token_verificador import token_verifica

parser = reqparse.RequestParser()
parser.add_argument('titulo', type=str, help='Problema no titulo', required=True)
parser.add_argument('descricao', type=str, help='Problema na descricao', required=True)
parser.add_argument('numero_time', type=int, help='Problema na quantidade', required=True)
parser.add_argument('meta_arrecadacao', type=float, help='Problema na meta_arrecadacao', required=True)
parser.add_argument('valor_arrecadado', type=float, help='Problema no valor_arrecadado', required=True)
parser.add_argument('conta_destino', type=str, help='Problema na conta de destino ', required=True)

class Campanhas(Resource):
    @token_verifica
    def get(self, tipo, refresh_token, id_campanha):
        if tipo != 'doador':
            message = Message("Acesso Não autorizado", 2)
            return marshal(message, message_fields), 401
        logger.info("Campanhas listadas com sucesso!")
        campanhas = Campanha.query.filter_by(id=id_campanha, status="Em andamento").first()
        return marshal(campanhas, campanha_fields), 200

    @token_verifica
    def post(self, tipo, refresh_token, id):
        if tipo != 'atleta':
            message = Message("Acesso não autorizado", 1)
            return  marshal(message, message_fields)
        args = parser.parse_args()
        try:
            titulo = args["titulo"]
            descricao = args["descricao"]
            numero_time = args["numero_time"]
            meta_arrecadacao = args["meta_arrecadacao"]
            valor_arrecadado = args["valor_arrecadado"]
            conta_destino = args["conta_destino"]

            if not titulo or len(titulo) < 3:
                logger.info("Título não informado ou não tem no mínimo 3 caracteres")
                message = Message("Título não informado ou não tem no mínimo 3 caracteres", 2)
                return marshal(message, message_fields), 400

            if not descricao or len(descricao) < 10:
                logger.info("Descrição não informada ou não tem no mínimo 10 caracteres")
                message = Message("Descrição não informada ou não tem no mínimo 10 caracteres", 2)
                return marshal(message, message_fields), 400

            if numero_time <= 0:
                logger.info("A quantidade inválida")
                message = Message("A quantidade invalida", 2)
                return marshal(message, message_fields), 400

            if meta_arrecadacao <= 0:
                logger.info("Meta de arrecadação deve ser um valor positivo")
                message = Message("Meta de arrecadação deve ser um valor maior que zero", 2)
                return marshal(message, message_fields), 400

            if valor_arrecadado < 0:
                logger.info("Valor arrecadado deve ser um valor positivo")
                message = Message("Valor arrecadado deve ser um valor positivo", 2)
                return marshal(message, message_fields), 400

            if not conta_destino or len(conta_destino) == 5:
                logger.info("A conta de destino deve ter 5 caracteres")
                message = Message("A conta de destino deve ter 5 caracteres", 2)
                return marshal(message, message_fields), 400

            campanha = Campanha(titulo, descricao, numero_time, meta_arrecadacao, valor_arrecadado, conta_destino, id)

            db.session.add(campanha)
            db.session.commit()

            logger.info("Campanha cadastrada com sucesso!")
            return marshal(campanha, campanha_fields), 201

        except Exception as e:
            logger.error(f"Error: {e}")
            message = Message("Erro ao cadastrar campanha", 2)
            return marshal(message, message_fields), 404

class CampanhasById(Resource):
    @token_verifica
    def get(self, tipo, refresh_token, id_usuario, id_campanha):
        if tipo != 'doador':
            message = Message("Acesso não autorizado", 1)
            return  marshal(message, message_fields)

        campanha = Campanha.query.filter_by(id=id_campanha,status="Em andamento").first()

        if campanha is None:
            logger.error(f"Campanha {id_campanha} não encontrada")
            message = Message(f"Campanha {id_campanha} não encontrada", 1)
            return marshal(message, message_fields), 404

        logger.info(f"Campanha {id_campanha} encontrada com sucesso!")
        return marshal(campanha, campanha_fields), 200

    @token_verifica
    def put(self, tipo, refresh_token, id_usuario, id_campanha):
        if tipo != 'atleta':
            message = Message("Acesso não autorizado", 1)
            return  marshal(message, message_fields)
            
        args = parser.parse_args()
        try:
            campanha = Campanha.query.get(id_campanha)
            if campanha is None:
                logger.error(f"Campanha {id_campanha} não encontrada")
                message = Message(f"Campanha {id_campanha} não encontrada", 1)
                return marshal(message, message_fields), 404

            titulo = args["titulo"]
            descricao = args["descricao"]
            numero_time = args["numero_time"]
            meta_arrecadacao = args["meta_arrecadacao"]
            valor_arrecadado = args["valor_arrecadado"]
            conta_destino = args["conta_destino"]

            if not titulo or len(titulo) < 3:
                logger.info("Título não informado ou não tem no mínimo 3 caracteres")
                message = Message("Título não informado ou não tem no mínimo 3 caracteres", 2)
                return marshal(message, message_fields), 400

            if not descricao or len(descricao) < 10:
                logger.info("Descrição não informada ou não tem no mínimo 10 caracteres")
                message = Message("Descrição não informada ou não tem no mínimo 10 caracteres", 2)
                return marshal(message, message_fields), 400

            if  numero_time <= 1:
                logger.info("A quantidade inválida")
                message = Message("A quantidade invalida", 2)
                return marshal(message, message_fields), 400

            if meta_arrecadacao < 0:
                logger.info("Meta de arrecadação deve ser um valor positivo")
                message = Message("Meta de arrecadação deve ser um valor positivo", 2)
                return marshal(message, message_fields), 400

            if valor_arrecadado < 0:
                logger.info("Valor arrecadado deve ser um valor positivo")
                message = Message("Valor arrecadado deve ser um valor positivo", 2)
                return marshal(message, message_fields), 400

            if not conta_destino or len(conta_destino) == 5:
                logger.info("A conta de destino deve ter 5 caracteres")
                message = Message("A conta de destino deve ter 5 caracteres", 2)
                return marshal(message, message_fields), 400

            campanha.titulo = titulo
            campanha.descricao = descricao
            campanha.numero_time = numero_time
            campanha.meta_arrecadacao = meta_arrecadacao
            campanha.valor_arrecadado = valor_arrecadado
            campanha.conta_destino = conta_destino

            db.session.add(campanha)
            db.session.commit()

            logger.info("Campanha atualizada com sucesso!")
            return marshal(campanha, campanha_fields), 200
        except Exception as e:
            logger.error(f"Error: {e}")
            message = Message("Erro ao atualizar a campanha", 2)
            return marshal(message, message_fields), 404

    @token_verifica    
    def delete(self, tipo, refresh_token, id_usuario, id_campanha):
        campanha = Campanha.query.filter_by(id=id_campanha, status="Em andamento").first()

        if campanha is None:
            logger.error(f"Campanha {id_campanha} não encontrada")
            message = Message(f"Campanha {id_campanha} não encontrada", 1)
            return marshal(message, message_fields), 404

        db.session.delete(campanha)
        db.session.commit()

        message = Message("Campanha deletada com sucesso!", 3)
        return marshal(message, message_fields), 200

class CampanhaByNome(Resource):
    def get(self, nome):
        campanha = Campanha.query.filter_by(titulo=nome, status="Em andamento").all()

        if not campanha:
            logger.error(f"Campanha {nome} não encontrada")
            message = Message(f"Campanha {nome} não encontrada", 1)
            return marshal(message, message_fields), 404

        logger.info(f"Campanha {nome} encontrada com sucesso!")
        return marshal(campanha, campanha_fields), 200

class CampanhaMe(Resource):
    def get(self):
        campanhas = Campanha.query.filter_by(status="Em andamento").all()

        if not campanhas:
            logger.error("Nenhuma campanha encontrada")
            message = Message("Nenhuma campanha encontrada", 1)
            return marshal(message, message_fields), 404

        logger.info("Campanhas encontradas com sucesso!")
        return marshal(campanhas, campanha_fields), 200

class CampanhaPagination(Resource):
  @token_verifica
  def get(self, tipo, refresh_token, id):
    if tipo != 'doador':
        message = Message("Acesso não autorizado", 1)
        return  marshal(message, message_fields)
    pageIndex = request.args.get("pageIndex", 1, type=int)
    perPage= request.args.get("per-page", 6, type=int)

    campanhas = Campanha.query.filter_by(status="Em andamento").all()
    campanhas_query = Campanha.query.order_by(desc(Campanha.created_at))
    campanhaPagination = campanhas_query.paginate(page=pageIndex, per_page=perPage, error_out=False)

    data = {"campanhas": campanhaPagination.items, "indiceDaPagina": pageIndex, "itemsPorPagina": perPage, "totalCampanhas": len(campanhas)}

    logger.info("Campanhas listados com sucesso")
    return marshal(data, campanhasFieldsPagination), 200
  
class CampanhaFinalizada(Resource):
    @token_verifica
    def get(self, tipo, refreshToken, usuario_id):
        if tipo != 'atleta':
            logger.error(f"Usuario nao autorizado")
            message = Message("Acesso não autorizado", 1)
            return  marshal(message, message_fields)

        campanha = Campanha.query.filter_by(atleta_id=usuario_id, status="Finalizada").all()
        
        logger.info("Campanha listada com sucesso")
        return marshal(campanha, campanha_fields), 200