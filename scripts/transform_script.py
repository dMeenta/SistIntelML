import pandas as pd
from pathlib import Path
import json

def main():
    input_path = Path("data/processed/riasec_processed.csv")
    output_path = Path("data/processed/answers_log.json")
    
    if not input_path.exists():
        raise FileNotFoundError(f"No se encontró {input_path}")
    
    df = pd.read_csv(input_path)
    
    # Transformación a formato JSON
    output_data = []
    for _, row in df.iterrows():
        record = {
            "answers": [row[f"Q{i+1}"] for i in range(48)],
            "student_info": {
                "age": row["age"],
                "gender": "M" if row["gender"] == 1 else "F",
                "country": row.get("country", "")
            },
            "profile": row["profile"]
        }
        output_data.append(record)
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f)
    
    print(f"✅ Datos transformados guardados en {output_path}")

if __name__ == "__main__":
    main()