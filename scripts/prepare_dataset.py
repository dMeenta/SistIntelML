from pathlib import Path
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from pathlib import Path
import pandas as pd
import numpy as np

def main():
    # Configurar paths
    raw_path = Path("data/raw/RIASEC")
    proc_path = Path("data/processed")
    proc_path.mkdir(parents=True, exist_ok=True)

    # Paso 1: Verificar archivo fuente
    csv_path = raw_path/"data.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"No se encontró {csv_path}")

    # Paso 2: Leer datos con manejo de tipos y valores faltantes
    try:
        # Definir tipos de columnas explícitamente
        dtype_dict = {
            'age': 'Int64',
            'gender': 'Int64',
            'country': 'string',
            'education': 'Int64',
            'urban': 'Int64'
        }
        
        # Columnas a leer (solo las que necesitamos)
        usecols = [
            'R1','R2','R3','R4','R5','R6','R7','R8',
            'I1','I2','I3','I4','I5','I6','I7','I8',
            'A1','A2','A3','A4','A5','A6','A7','A8',
            'S1','S2','S3','S4','S5','S6','S7','S8',
            'E1','E2','E3','E4','E5','E6','E7','E8',
            'C1','C2','C3','C4','C5','C6','C7','C8',
            'age', 'gender', 'country'
        ]
        
        df = pd.read_csv(
            csv_path,
            sep='\t',
            dtype=dtype_dict,
            usecols=usecols,
            na_values=['', 'NA', 'N/A', ' ']
        )
    except Exception as e:
        raise ValueError(f"Error al leer el archivo CSV: {str(e)}")

    # Paso 3: Limpieza y normalización de datos
    # Convertir país a mayúsculas y eliminar espacios
    df['country'] = df['country'].str.upper().str.strip()
    
    # Manejar valores faltantes en edad y género
    df = df.dropna(subset=['age', 'gender', 'country'])
    
    # Paso 4: Aplicar filtros específicos
    # Filtro 1: Edad > 15 años
    # Filtro 2: País = Perú (PE o PERU según formato real)
    filtered_df = df[
        (df['age'] > 15) & 
        (df['gender'].isin([1, 2]))  # 1=Masculino, 2=Femenino
    ].copy()

    if filtered_df.empty:
        raise ValueError("No hay datos que cumplan los criterios (edad > 15 y género válido)")

    # Paso 5: Definir columnas RIASEC (48 preguntas)
    riasec_columns = (
        [f'R{i}' for i in range(1,9)] + 
        [f'I{i}' for i in range(1,9)] + 
        [f'A{i}' for i in range(1,9)] + 
        [f'S{i}' for i in range(1,9)] + 
        [f'E{i}' for i in range(1,9)] + 
        [f'C{i}' for i in range(1,9)]
    )

    # Paso 6: Validar respuestas RIASEC (1-5)
    for col in riasec_columns:
        # Convertir a numérico y reemplazar valores fuera de rango con NaN
        filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')
        filtered_df[col] = filtered_df[col].apply(lambda x: x if 1 <= x <= 5 else np.nan)
    
    # Eliminar registros con respuestas RIASEC no válidas
    filtered_df = filtered_df.dropna(subset=riasec_columns)

    # Paso 7: Calcular puntajes RIASEC
    riasec_scores = {
        'R': filtered_df[[f'R{i}' for i in range(1,9)]].mean(axis=1),
        'I': filtered_df[[f'I{i}' for i in range(1,9)]].mean(axis=1),
        'A': filtered_df[[f'A{i}' for i in range(1,9)]].mean(axis=1),
        'S': filtered_df[[f'S{i}' for i in range(1,9)]].mean(axis=1),
        'E': filtered_df[[f'E{i}' for i in range(1,9)]].mean(axis=1),
        'C': filtered_df[[f'C{i}' for i in range(1,9)]].mean(axis=1)
    }

    # Paso 8: Asignar perfil dominante
    filtered_df['profile'] = pd.DataFrame(riasec_scores).idxmax(axis=1)

    # Paso 9: Preparar dataset final
    output_df = filtered_df[['age', 'gender', 'country'] + riasec_columns + ['profile']].copy()
    
    # Convertir género a M/F
    output_df['gender'] = output_df['gender'].map({1: 'M', 2: 'F'})
    
    # Renombrar columnas de preguntas a Q1-Q48
    new_columns = ['age', 'gender', 'country'] + [f'Q{i}' for i in range(1,49)] + ['profile']
    output_df.columns = new_columns

    # Paso 10: Guardar datos procesados
    output_df.to_csv(proc_path/"riasec_processed.csv", index=False)
    
    # Generar reporte de procesamiento
    report = {
        'total_original': len(df),
        'total_filtered': len(output_df),
        'age_distribution': {
            'min': int(output_df['age'].min()),
            'max': int(output_df['age'].max()),
            'mean': float(output_df['age'].mean())
        },
        'gender_distribution': output_df['gender'].value_counts().to_dict(),
        'profile_distribution': output_df['profile'].value_counts().to_dict()
    }
    
    print("\n=== Reporte de Procesamiento ===")
    print(f"Registros originales: {report['total_original']}")
    print(f"Registros después de filtros: {report['total_filtered']}")
    print(f"Distribución por edad: {report['age_distribution']}")
    print(f"Distribución por género: {report['gender_distribution']}")
    print(f"Distribución de perfiles RIASEC: {report['profile_distribution']}")
    print(f"\n✅ Datos guardados en: {proc_path/'riasec_processed.csv'}")

if __name__ == "__main__":
    main()