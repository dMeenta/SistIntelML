from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess
import seaborn as sns

# Configuración de paths
DATA_RAW = Path("data/raw/RIASEC")
DATA_PROC = Path("data/processed")
DATA_TRAIN = Path("data/training")
MODELS_DIR = Path("ml_models")
PLOTS_DIR = Path("visualizations")

def prepare_initial_data():
    """Prepara los datos iniciales desde OpenPsychometrics"""
    print("⚠️ Preparando datos iniciales...")
    
    try:
        # Paso 1: Ejecutar el script de preparación
        if not (DATA_PROC/"riasec_processed.csv").exists():
            print("Ejecutando prepare_dataset.py...")
            subprocess.run(["python", "scripts/prepare_dataset.py"], check=True)
        
        # Paso 2: Transformar a formato JSON
        if not (DATA_PROC/"answers_log.json").exists():
            print("Ejecutando transform_script.py...")
            subprocess.run(["python", "scripts/transform_script.py"], check=True)
        
        # Paso 3: Convertir a CSV de entrenamiento
        if not (DATA_TRAIN/"answers_log.csv").exists():
            print("Generando CSV de entrenamiento...")
            with open(DATA_PROC/"answers_log.json") as f:
                data = pd.read_json(f)
            
            # Convertir a formato CSV plano
            answer_cols = [f"answer_{i+1}" for i in range(48)]
            rows = []
            for record in data.to_dict('records'):
                row = {f"answer_{i+1}": record['answers'][i] for i in range(48)}
                row.update({
                    "age": record['student_info']['age'],
                    "gender": record['student_info']['gender'],
                    "profile": record['profile']
                })
                rows.append(row)
            
            DATA_TRAIN.mkdir(exist_ok=True)
            pd.DataFrame(rows).to_csv(DATA_TRAIN/"answers_log.csv", index=False)
            
        print("✅ Datos iniciales preparados correctamente")
        
    except Exception as e:
        print(f"❌ Error preparando datos iniciales: {e}")
        raise

def train_model():
    """Entrena el modelo con los datos disponibles"""
    # Asegurar que los directorios existen
    for dir_path in [DATA_RAW, DATA_PROC, DATA_TRAIN, MODELS_DIR, PLOTS_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Paso 1: Preparar datos si no existen
    if not (DATA_TRAIN/"answers_log.csv").exists():
        prepare_initial_data()
        if not (DATA_TRAIN/"answers_log.csv").exists():
            raise FileNotFoundError("No se pudo generar el archivo de entrenamiento")

    # Paso 2: Cargar datos
    try:
        df = pd.read_csv(DATA_TRAIN/"answers_log.csv")
        print(f"📊 Dataset cargado con {len(df)} registros")
        
        # Verificar estructura
        answer_cols = [col for col in df.columns if col.startswith("answer_")]
        if len(answer_cols) != 48:
            raise ValueError(f"Se esperaban 48 columnas de respuestas, se encontraron {len(answer_cols)}")
        
        # Limpieza básica
        df = df.dropna(subset=answer_cols + ['profile'])
        
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")
        raise

    # Paso 3: Preparar datos para entrenamiento
    X = df[answer_cols].values
    y = df["profile"].values
    classes = sorted(np.unique(y))
    
    # División train-test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    # Paso 4: Configurar modelo
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=5,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    
    # Paso 5: Entrenamiento
    print("🏋️ Entrenando modelo...")
    model.fit(X_train, y_train)
    
    # Paso 6: Evaluación
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    # --- NUEVO: Generación de gráficos ---
    PLOTS_DIR.mkdir(exist_ok=True)
    
    # 1. Matriz de confusión
    plt.figure(figsize=(10, 8))
    cm = confusion_matrix(y_test, y_pred, labels=classes)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=classes, yticklabels=classes)
    plt.title('Matriz de Confusión')
    plt.ylabel('Verdaderos')
    plt.xlabel('Predichos')
    plt.savefig(PLOTS_DIR/'confusion_matrix.png')
    plt.close()
    
    # 2. Importancia de características
    plt.figure(figsize=(12, 6))
    feat_importances = pd.Series(model.feature_importances_, index=answer_cols)
    feat_importances.nlargest(15).plot(kind='barh')
    plt.title('Top 15 Preguntas Más Importantes')
    plt.savefig(PLOTS_DIR/'feature_importance.png')
    plt.close()
    
    # 3. Distribución de clases
    plt.figure(figsize=(8, 6))
    pd.Series(y).value_counts().plot(kind='bar')
    plt.title('Distribución de Perfiles RIASEC')
    plt.xlabel('Perfil')
    plt.ylabel('Frecuencia')
    plt.savefig(PLOTS_DIR/'class_distribution.png')
    plt.close()
    
    # 4. Precisión por clase (del classification report)
    report = classification_report(y_test, y_pred, output_dict=True)
    class_metrics = pd.DataFrame(report).transpose().iloc[:-3, :3]
    plt.figure(figsize=(10, 6))
    class_metrics.plot(kind='bar', rot=0)
    plt.title('Métricas por Perfil')
    plt.legend(loc='lower right')
    plt.savefig(PLOTS_DIR/'class_metrics.png')
    plt.close()
    
    # Paso 7: Guardar modelo
    MODELS_DIR.mkdir(exist_ok=True)
    model_path = MODELS_DIR/"riasec_model.pkl"
    joblib.dump(model, model_path)
    
    # Paso 8: Guardar metadatos
    metadata = {
        "accuracy": accuracy,
        "train_date": datetime.now(timezone.utc).isoformat(),
        "classes_distribution": pd.Series(y).value_counts().to_dict(),
        "features_importance": dict(zip(answer_cols, model.feature_importances_))
    }
    
    with open(MODELS_DIR/"model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✅ Modelo entrenado y guardado en {model_path}")
    print(f"   - Exactitud: {accuracy:.2%}")
    print(f"   - Muestras totales: {len(X)}")
    print(f"   - Distribución de clases:\n{pd.Series(y).value_counts().to_string()}")
    
    return model_path

if __name__ == "__main__":
    train_model()