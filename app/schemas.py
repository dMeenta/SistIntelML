from pydantic import BaseModel
from typing import List
from enum import Enum

class Gender(str, Enum):
    male = "M"
    female = "F"

class StudentInfo(BaseModel):
    name: str
    age: int
    gender: Gender
    school: str

class TestInput(BaseModel):
    answers: List[int]
    student_info: StudentInfo
