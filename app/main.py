from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.schemas import TestInput, TestResult, FeedbackInput
from app.services import model_service
from typing import AsyncIterator
import logging
from datetime import datetime, timezone

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manejador del ciclo de vida de la aplicación"""
    # Código de inicio (antes de yield)
    logger.info("Iniciando aplicación...")
    
    # Verificar que el modelo está cargado
    try:
        logger.info(f"Modelo cargado desde {model_service.model.model_path}")
    except Exception as e:
        logger.error(f"Error al cargar el modelo: {str(e)}")
        raise
    
    yield  # La aplicación está lista para recibir requests
    
    # Código de cierre (después de yield)
    logger.info("Deteniendo aplicación...")
    # Aquí podrías añadir lógica de limpieza si es necesario

app = FastAPI(
    title="Sistema de Test Vocacional RIASEC",
    description="API para el test vocacional basado en el modelo de Holland",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan  # Usamos el nuevo sistema de lifespan
)

# Configuración CORS (ajusta según tus necesidades)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica tus dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/predict", response_model=TestResult)
async def predict(
    input_data: TestInput,
    background_tasks: BackgroundTasks
):
    """
    Endpoint para realizar predicciones vocacionales
    
    Args:
        answers: Lista de 48 respuestas (1-5 Likert scale)
        student_info: Información demográfica del estudiante
    
    Returns:
        TestResult: Perfil RIASEC, probabilidades y carreras recomendadas
    """
    try:
        logger.info(f"Nueva predicción para {input_data.student_info.first_name}")
        
        # Realizar predicción
        result = model_service.predict_and_store(input_data)
        
        # Programar reentrenamiento asíncrono si hay suficientes datos
        background_tasks.add_task(check_retraining)
        
        return result
        
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Ocurrió un error al procesar el test"
        )

@app.post("/api/feedback/{test_id}")
async def submit_feedback(
    test_id: str,
    feedback: FeedbackInput
):
    """
    Endpoint para recibir feedback sobre los resultados
    
    Args:
        test_id: ID del test en MongoDB
        feedback: Datos de satisfacción y perfil real (opcional)
    """
    try:
        logger.info(f"Recibido feedback para test {test_id}")
        return model_service.submit_feedback(feedback, test_id)
    except Exception as e:
        logger.error(f"Error al procesar feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/retrain")
async def retrain_model():
    """
    Endpoint para forzar el reentrenamiento del modelo
    
    Returns:
        dict: Resultados del reentrenamiento
    """
    try:
        logger.info("Solicitado reentrenamiento manual")
        result = model_service.retrain_model()
        
        if result["status"] == "not_retrained":
            logger.info(result["reason"])
            return {"status": "skipped", "reason": result["reason"]}
            
        logger.info(
            f"Modelo reentrenado - Accuracy: {result['accuracy']:.2%} "
            f"con {result['samples']} muestras"
        )
        return result
        
    except Exception as e:
        logger.error(f"Error en reentrenamiento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Endpoint de verificación de estado"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model_version": model_service.last_retrain_date or "initial",
        "model_accuracy": getattr(model_service.model, "last_accuracy", None)
    }

async def check_retraining():
    """Verifica si se debe reentrenar el modelo"""
    try:
        if model_service.should_retrain():
            result = model_service.retrain_model()
            logger.info(
                f"Reentrenamiento automático completado. "
                f"Accuracy: {result['accuracy']:.2%}"
            )
    except Exception as e:
        logger.error(f"Error en reentrenamiento automático: {str(e)}")