import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import predict
from app.exceptions.handlers import register_exception_handlers


app = FastAPI(
  title="Sistema inteligente para la clasificación del perfil vocacional basado en el modelo RIASEC utilizando razonamiento simbólico",
  description="Sistema backend para predecir perfiles profesionales según el modelo RIASEC utilizando LightGBM",
  version="1.0.0"
)

FRONTEND_URL = os.environ.get("FRONTEND")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # ¡Sin barra al final!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(predict.router)