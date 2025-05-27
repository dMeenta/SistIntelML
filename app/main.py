from fastapi import FastAPI, BackgroundTasks
from app.schemas import TestInput
from app.services import predict_and_store, retrain_model_background

app = FastAPI()

@app.post("/predict")
async def predict(input_data: TestInput, background_tasks: BackgroundTasks):
    profile = predict_and_store(input_data)
    background_tasks.add_task(retrain_model_background)
    return {"profile": profile}
