
from pathlib import Path
import pandas as pd


class DataLoader:
    """
    Carga y prepara los datos del desafío QualyData.
    """

    def __init__(self, data_dir="datos/practica"):
        self.data_dir = Path(data_dir)

    def load_csv(self, filename):
        """Carga un archivo CSV o CSV comprimido."""
        file_path = self.data_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"No se encontró el archivo: {file_path}"
            )

        return pd.read_csv(file_path)

    def load_sources(self):
        return self.load_csv("fuentes.csv")

    def load_publications(self):
        return self.load_csv("publicaciones.csv.gz")

    def load_comments(self):
        return self.load_csv("comentarios.csv.gz")

    def load_accounts(self):
        return self.load_csv("cuentas.csv.gz")

    def load_all(self):
        """Carga todos los conjuntos de datos."""
        print("Cargando datos de QualyData...")

        data = {
            "fuentes": self.load_sources(),
            "publicaciones": self.load_publications(),
            "comentarios": self.load_comments(),
            "cuentas": self.load_accounts()
        }

        print("\nDatos cargados correctamente:")

        for name, dataframe in data.items():
            print(f"{name}: {len(dataframe)} registros")

        return data

    def inspect(self, data):
        """Muestra información básica de cada conjunto."""
        for name, dataframe in data.items():
            print(f"\n--- {name.upper()} ---")
            print("Columnas:", list(dataframe.columns))
            print("Valores nulos:")
            print(dataframe.isnull().sum())


if __name__ == "__main__":
    loader = DataLoader()
    datasets = loader.load_all()
    loader.inspect(datasets)
