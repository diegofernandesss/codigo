from datetime import datetime, timedelta
from model.pessoa import*
import jwt
import time

class TokenCriador:
    def __init__(self, token_key: str, exp_time_hrs: int, refresh_time_hrs:int):
        self.__TOKEN_KEY = token_key
        self.__EXP_TIME_HRS = exp_time_hrs
        self.__REFRESH_TIME_HRS = refresh_time_hrs


    def create(self, tipo:str, id:int):
        return self.__encode_token(tipo, id)

    def refresh(self, token: str):

        token_informacao = jwt.decode(token,key = self.__TOKEN_KEY, algorithms="HS256")
        tipo = token_informacao["tipo"]
        exp_time =  token_informacao["exp"]

        if ((exp_time - time.time()) /3600) < self.__REFRESH_TIME_HRS:
            return self.__enconde_token(tipo)
        return token

    def __encode_token(self, tipo:str, id:int):
       token = jwt.encode({
            'exp': datetime.utcnow() + timedelta(hours=self.__EXP_TIME_HRS),
            'id': id,
            'tipo': tipo
        }, key = self.__TOKEN_KEY,algorithm="HS256")

       return token