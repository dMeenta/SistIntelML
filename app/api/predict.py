from fastapi import APIRouter
from app.models.user_response_model import UserRequest
from app.services.prediction_service import predict_major
from app.db.mongo import db

router = APIRouter()

@router.post("/predict", responses={
    200: {"description": "Predicción exitosa"},
    422: {"description": "Datos faltantes o inválidos"},
    400: {"description": "Error de predicción"},
    500: {"description": "Error interno del servidor"},
})
async def predict_route(request: UserRequest):
    result = predict_major(request.user_test_answers, request.name)
    major = result["major"]
    symbolic_reasoning = result["symbolic_reasoning"]

    await db["user_answers"].insert_one({
        "answers": request.user_test_answers.model_dump(),
        "predicted_major": major
    })

    return {
        "name": request.name,
        "last_name": request.last_name,
        "predicted_major": major,
        "symbolic_reasoning": symbolic_reasoning,
        "feedback": result["feedback"]
    }