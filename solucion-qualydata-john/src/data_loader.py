from pathlib import Path
import pandas as pd

class DataLoader:
    """Carga los datos buscando automáticamente la carpeta datos/practica."""

    def __init__(self, data_dir=None):
        if data_dir is None:
            # Sube por el árbol de directorios hasta encontrar la carpeta 'datos/practica'
            current = Path(__file__).resolve().parent
            found_dir = None
            for _ in range(4):
                candidate = current / "datos" / "practica"
                if candidate.exists():
                    found_dir = candidate
                    break
                current = current.parent
            
            self.data_dir = found_dir if found_dir else Path(__file__).resolve().parent.parent / "datos" / "practica"
        else:
            self.data_dir = Path(data_dir)

    def load_csv(self, filename: str) -> pd.DataFrame:
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            gz_path = self.data_dir / f"{filename}.gz"
            if gz_path.exists():
                file_path = gz_path
            else:
                raise FileNotFoundError(f"No se encontró el archivo: {file_path}")

        print(f"Cargando {file_path.name}...")
        return pd.read_csv(file_path)

    def load_sources(self) -> pd.DataFrame:
        return self.load_csv("fuentes.csv")

    def load_posts(self) -> pd.DataFrame:
        return self.load_csv("publicaciones.csv")

    def load_accounts(self) -> pd.DataFrame:
        return self.load_csv("cuentas.csv")

    def load_comments(self) -> pd.DataFrame:
        return self.load_csv("comentarios.csv")

    def load_all(self) -> dict:
        return {
            "fuentes": self.load_sources(),
            "publicaciones": self.load_posts(),
            "cuentas": self.load_accounts(),
            "comentarios": self.load_comments(),
        }