from typing import Annotated
from pydantic import BaseModel, Field

class UserTestAnswers(BaseModel):
    # Ítems RIASEC: valores de 1 a 5
    R1: Annotated[int, Field(ge=1, le=5, strict=True)]
    R2: Annotated[int, Field(ge=1, le=5, strict=True)]
    R3: Annotated[int, Field(ge=1, le=5, strict=True)]
    R4: Annotated[int, Field(ge=1, le=5, strict=True)]
    R5: Annotated[int, Field(ge=1, le=5, strict=True)]
    R6: Annotated[int, Field(ge=1, le=5, strict=True)]
    R7: Annotated[int, Field(ge=1, le=5, strict=True)]
    R8: Annotated[int, Field(ge=1, le=5, strict=True)]

    I1: Annotated[int, Field(ge=1, le=5, strict=True)]
    I2: Annotated[int, Field(ge=1, le=5, strict=True)]
    I3: Annotated[int, Field(ge=1, le=5, strict=True)]
    I4: Annotated[int, Field(ge=1, le=5, strict=True)]
    I5: Annotated[int, Field(ge=1, le=5, strict=True)]
    I6: Annotated[int, Field(ge=1, le=5, strict=True)]
    I7: Annotated[int, Field(ge=1, le=5, strict=True)]
    I8: Annotated[int, Field(ge=1, le=5, strict=True)]

    A1: Annotated[int, Field(ge=1, le=5, strict=True)]
    A2: Annotated[int, Field(ge=1, le=5, strict=True)]
    A3: Annotated[int, Field(ge=1, le=5, strict=True)]
    A4: Annotated[int, Field(ge=1, le=5, strict=True)]
    A5: Annotated[int, Field(ge=1, le=5, strict=True)]
    A6: Annotated[int, Field(ge=1, le=5, strict=True)]
    A7: Annotated[int, Field(ge=1, le=5, strict=True)]
    A8: Annotated[int, Field(ge=1, le=5, strict=True)]

    S1: Annotated[int, Field(ge=1, le=5, strict=True)]
    S2: Annotated[int, Field(ge=1, le=5, strict=True)]
    S3: Annotated[int, Field(ge=1, le=5, strict=True)]
    S4: Annotated[int, Field(ge=1, le=5, strict=True)]
    S5: Annotated[int, Field(ge=1, le=5, strict=True)]
    S6: Annotated[int, Field(ge=1, le=5, strict=True)]
    S7: Annotated[int, Field(ge=1, le=5, strict=True)]
    S8: Annotated[int, Field(ge=1, le=5, strict=True)]

    E1: Annotated[int, Field(ge=1, le=5, strict=True)]
    E2: Annotated[int, Field(ge=1, le=5, strict=True)]
    E3: Annotated[int, Field(ge=1, le=5, strict=True)]
    E4: Annotated[int, Field(ge=1, le=5, strict=True)]
    E5: Annotated[int, Field(ge=1, le=5, strict=True)]
    E6: Annotated[int, Field(ge=1, le=5, strict=True)]
    E7: Annotated[int, Field(ge=1, le=5, strict=True)]
    E8: Annotated[int, Field(ge=1, le=5, strict=True)]

    C1: Annotated[int, Field(ge=1, le=5, strict=True)]
    C2: Annotated[int, Field(ge=1, le=5, strict=True)]
    C3: Annotated[int, Field(ge=1, le=5, strict=True)]
    C4: Annotated[int, Field(ge=1, le=5, strict=True)]
    C5: Annotated[int, Field(ge=1, le=5, strict=True)]
    C6: Annotated[int, Field(ge=1, le=5, strict=True)]
    C7: Annotated[int, Field(ge=1, le=5, strict=True)]
    C8: Annotated[int, Field(ge=1, le=5, strict=True)]

    # Extra features
    age: Annotated[int, Field(le=80, strict=True)]
    gender: Annotated[int, Field(ge=1, le=3, strict=True)]  # 1 = male, 2 = female, 3 = other

    def to_model_input(self):
        riasec_order = [f"{dim}{i}" for dim in "RIASEC" for i in range(1, 9)]
        return [getattr(self, col) for col in riasec_order + ["age", "gender"]]
    

class UserRequest(BaseModel):
  name: str
  last_name: str
  user_test_answers: UserTestAnswers