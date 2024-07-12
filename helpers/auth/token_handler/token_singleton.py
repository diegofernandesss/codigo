from .token_criador import TokenCriador
from helpers.config.jwt_config_file import jwt_config

token_criador = TokenCriador(
  token_key=jwt_config["TOKEN_KEY"],
  exp_time_hrs=jwt_config["EXP_TIME_HRS"],
  refresh_time_hrs=jwt_config["REFRESH_TIME_HRS"]
)