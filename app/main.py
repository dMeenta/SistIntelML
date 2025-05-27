from fastapi import FastAPI
from app.schemas import TestInput
from app.model import predict_profile
from app.storage import save_result

app = FastAPI()

@app.post("/predict")
async def predict(input_data: TestInput):
    profile = predict_profile(input_data.answers)
    save_result(input_data.answers, profile, input_data.student_info)
    return {"profile": profile}
