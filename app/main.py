from fastapi import FastAPI
from api import predict
from exceptions.handlers import register_exception_handlers

app = FastAPI(
  title="Sistema inteligente para la clasificación del perfil vocacional basado en el modelo RIASEC utilizando razonamiento simbólico",
  description="Sistema backend para predecir perfiles profesionales según el modelo RIASEC utilizando LightGBM",
  version="1.0.0"
)
register_exception_handlers(app)

app.include_router(predict.router)