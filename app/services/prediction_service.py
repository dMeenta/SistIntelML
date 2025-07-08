import joblib
from app.models.user_response_model import UserTestAnswers
from app.symbolic.engine import VocationalEngine

EXPLANATIONS = {
    "REALISTIC": "Preferencia por actividades prácticas y manuales",
    "INVESTIGATIVE": "Interés en resolver problemas y pensar analíticamente",
    "ARTISTIC": "Expresión creativa y sensibilidad estética",
    "SOCIAL": "Disposición para ayudar, enseñar y colaborar con otros",
    "ENTERPRISING": "Gusto por liderar, persuadir y emprender",
    "CONVENTIONAL": "Preferencia por el orden, la organización y datos"
}

DIM_TO_NAME = {
    "R": "REALISTIC",
    "I": "INVESTIGATIVE",
    "A": "ARTISTIC",
    "S": "SOCIAL",
    "E": "ENTERPRISING",
    "C": "CONVENTIONAL"
}

model = joblib.load("model/model_lgbm.pkl")
encoder = joblib.load("model/label_encoder_lgbm.pkl")

def build_feedback(name: str, profile: str, explanation: str) -> str:
    if profile == "MIXED":
        return f"{name}, tu perfil es mixto. Has mostrado intereses balanceados en varias dimensiones del modelo RIASEC."
    elif "-" in profile:
        return f"{name}, tienes un perfil combinado: {profile}. Esto sugiere intereses diversos. {explanation}"
    else:
        return f"{name}, tu perfil principal es {profile}. {explanation}"

def predict_major(user_answers: UserTestAnswers, name: str):
    X = [user_answers.to_model_input()]
    y_pred = model.predict(X)[0]
    major = encoder.inverse_transform([y_pred])[0]

    dimensions = "RIASEC"
    scores = {
        dim: sum(getattr(user_answers, f"{dim}{i}") for i in range(1, 9)) for dim in dimensions
    }

    engine = VocationalEngine()
    inferred_profile, rules = engine.infer_profile(scores)

    # Convertir a mayúscula para que coincida con DIM_TO_NAME
    activated_dims = set(rule.split(":")[0].split("_")[-1][0].upper() for rule in rules)

    if activated_dims:
        profile_key = "-".join(sorted(activated_dims))
        profile = "-".join(DIM_TO_NAME[dim] for dim in sorted(activated_dims))
        explanation = ". ".join(
            EXPLANATIONS[DIM_TO_NAME[dim]] for dim in sorted(activated_dims)
        )
        top_dims = list(activated_dims)
    else:
        # Respaldo por estadística
        max_score = max(scores.values())
        top_dims = [dim for dim, val in scores.items() if val == max_score]
        if len(top_dims) == 1:
            profile_key = top_dims[0]
            profile = DIM_TO_NAME[profile_key]
            explanation = EXPLANATIONS.get(profile, "")
        else:
            profile_key = "-".join(top_dims)
            profile = "MIXED"
            explanation = "Perfil combinado con altos puntajes en: " + ", ".join(top_dims)

    symbolic_reasoning = {
        "profile": profile,
        "scores": {dim: scores[dim] for dim in top_dims},
        "explanation": explanation,
        "activated_rules": rules
    }

    return {
        "major": major,
        "symbolic_reasoning": symbolic_reasoning,
        "feedback": build_feedback(name, profile, explanation)
    }