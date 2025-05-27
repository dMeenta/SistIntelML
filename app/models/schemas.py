from pydantic import BaseModel
from typing import List

class TestInput(BaseModel):
    answers: List[int]

class PredictionOutput(BaseModel):
    profile: str