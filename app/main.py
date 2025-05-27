from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.input import TestInput
from app.ml.predictor import predict_riasec
from app.services.storage import save_result
from app.services.storage import save_result


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
async def get_prediction(input_data: TestInput):
    profile = predict_riasec(input_data.answers)
    save_result(input_data.answers, profile)
    return {"profile": profile}
