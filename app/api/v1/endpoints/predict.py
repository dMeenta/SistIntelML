from fastapi import APIRouter, Depends
from app.models.schemas import TestInput, PredictionOutput
from app.services.predictor import predict_riasec

router = APIRouter()

@router.post("/predict", response_model=PredictionOutput)
async def predict(input_data: TestInput):
    profile = predict_riasec(input_data.answers)
    return {"profile": profile}
