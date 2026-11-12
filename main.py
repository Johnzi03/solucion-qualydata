import sys
import time
import json
from pathlib import Path

# Localizar automáticamente la carpeta del proyecto que contiene 'src'
current_file = Path(__file__).resolve()
possible_dirs = [
    current_file.parent,
    current_file.parent / "solucion-qualydata-john",
]

BASE_DIR = None
for p in possible_dirs:
    if (p / "src").exists():
        BASE_DIR = p
        break

if BASE_DIR is None:
    raise FileNotFoundError("No se encontró la carpeta 'src' en la estructura del proyecto.")

# Agregar carpetas de código al path de Python
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

from data_loader import DataLoader
from narrative_engine import NarrativeEngine
from network_engine import NetworkEngine

def main():
    start_time = time.time()
    output_dir = BASE_DIR / "entrega"
    output_dir.mkdir(exist_ok=True)

    print("=== INICIANDO PIPELINE QUALYDATA ===")

    # 1. Cargar datos
    loader = DataLoader(data_dir=BASE_DIR / "datos" / "practica")
    datasets = loader.load_all()

    # 2. Tarea A: Narrativas y Posturas
    narrative_eng = NarrativeEngine()
    df_comentarios, df_narrativas = narrative_eng.process(datasets["comentarios"])

    # 3. Tarea B: Coordinación de Cuentas
    network_eng = NetworkEngine()
    df_cuentas = network_eng.process(df_comentarios)

    # 4. Formatear y exportar entregables
    print("\nGuardando entregables en la carpeta entrega/...")
    
    # comentarios.csv
    df_out_comentarios = df_comentarios.rename(columns={"comentario_id": "id_comentario"})
    df_out_comentarios[["id_comentario", "id_narrativa", "postura"]].to_csv(
        output_dir / "comentarios.csv", index=False
    )
    
    # narrativas.csv
    df_narrativas.to_csv(output_dir / "narrativas.csv", index=False)

    # cuentas.csv
    df_cuentas.to_csv(output_dir / "cuentas.csv", index=False)

    # costo.json
    elapsed = round(time.time() - start_time, 2)
    metrics = {
        "tiempo_segundos": elapsed,
        "tokens_entrada": 0,
        "tokens_salida": 0,
        "costo_usd": 0.0,
        "hardware_usado": "Local CPU",
        "almacenamiento": "Local DataFrames"
    }
    with open(output_dir / "costo.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n Pipeline ejecutado con éxito en {elapsed} segundos.")

if __name__ == "__main__":
    main()