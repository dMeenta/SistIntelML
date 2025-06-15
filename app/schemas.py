from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class Gender(str, Enum):
    male = "M"
    female = "F"
class SchoolType(str, Enum):
    public = "public"
    private = "private"

class RIASEC(str, Enum):
    R = "R"  # Realista
    I = "I"  # Investigador
    A = "A"  # Artístico
    S = "S"  # Social
    E = "E"  # Emprendedor
    C = "C"  # Convencional

class StudentInfo(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    age: int = Field(..., gt=10, lt=100)
    gender: Gender
    school: str = Field(..., min_length=2, max_length=100)
    school_type: SchoolType
    email: Optional[str] = None

class TestInput(BaseModel):
    answers: List[int] = Field(..., min_items=48, max_items=48)
    student_info: StudentInfo

class TestResult(BaseModel):
    profile: RIASEC
    probabilities: Dict[RIASEC, float]
    dominant_traits: Dict[str, float]
    recommended_careers: List[str]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc()))

class FeedbackInput(BaseModel):
    satisfaction: int = Field(..., ge=1, le=5)
    comments: Optional[str] = None
    actual_profile: Optional[RIASEC] = None