import os
from dotenv import load_dotenv
from flask_restful import Api
from flask import Flask, Blueprint

from helpers.cors import cors
from helpers.database import db, migrate

#Importação dos models e resources
from resources.pessoa import Pessoas, PessoaByNome
from resources.doador import Doadores, DoadorById, updatedInfoPaymentDoador, DoadorInfo
from resources.campanha import Campanhas, CampanhasById, CampanhaPagination
from resources.atleta import Atletas, AtletaById, AtletaCampaigns, AtletaInfo, CampanhaAtletaById
from resources.login import Login
from resources.logout import Logout
from resources.doacao import DoacoesCampanha, DoacoesDoador, HistoricoDoacoesAtleta
from os import getenv
from resources.doacao import mail
load_dotenv()

# create the app
app = Flask(__name__)

# restful
api_bp = Blueprint('api', __name__)
api = Api(api_bp, prefix="/api")

postgresUser = os.getenv("POSTGRES_USER")
postgresPassword = os.getenv("POSTGRES_PASSWORD")

DB_URL = f"postgresql://{postgresUser}:{postgresPassword}@localhost:5432/athleteaid"
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = getenv('EMAIL_PASS')


# initialize the app with the extension
db.init_app(app)
cors.init_app(app)
migrate.init_app(app, db)
mail.init_app(app)

#Rotas
api.add_resource(Pessoas, '/pessoas')

api.add_resource(Doadores, '/doadores')
api.add_resource(DoadorInfo, '/doadorinfo')
api.add_resource(DoadorById,'/doadores/<int:id>')
api.add_resource(DoacoesCampanha, '/doacoes-campanha')
api.add_resource(DoacoesDoador, '/doacoes-doador') #Histórico das doações que o doador fez
api.add_resource(updatedInfoPaymentDoador, '/doador/infoPagamento')
api.add_resource(HistoricoDoacoesAtleta, '/historico-campanha') #Histórico das doações que recebeu


api.add_resource(Campanhas, '/campanhas')
api.add_resource(CampanhaPagination, '/campanha')
api.add_resource(CampanhasById, '/campanhas/<int:id_campanha>')

api.add_resource(Atletas, '/atletas')
api.add_resource(AtletaCampaigns, '/atleta-campanhas')
api.add_resource(AtletaById, '/atletas/<int:id>')
api.add_resource(AtletaInfo, '/atletainfo')
api.add_resource(CampanhaAtletaById, '/campanha-atleta/<int:id>')


api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
#api.add_resource(Imagem, '/upload')

# Blueprints para Restful
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
