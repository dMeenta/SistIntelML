from pydantic import BaseModel
from typing import List

class TestInput(BaseModel):
    answers: List[int]  # 60 respuestas del test RIASEC
