import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
import hdbscan

class NarrativeEngine:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.cache_dir = Path(__file__).resolve().parent.parent / ".cache"

    def _get_embeddings(self, texts: list) -> np.ndarray:
        self.cache_dir.mkdir(exist_ok=True)
        sig = f"{self.model_name}_{len(texts)}_{texts[0] if texts else ''}_{texts[-1] if texts else ''}"
        cache_hash = hashlib.md5(sig.encode("utf-8")).hexdigest()[:12]
        cache_file = self.cache_dir / f"embeddings_{cache_hash}.npy"

        if cache_file.exists():
            print(f"Cargando embeddings desde caché ({cache_file.name})...")
            return np.load(cache_file)

        print("Cargando modelo de embeddings...")
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)

        print("Generando embeddings de texto para los comentarios...")
        embeddings = self.model.encode(texts, batch_size=256, show_progress_bar=True)
        np.save(cache_file, embeddings)
        return embeddings

    def process(self, df_comentarios: pd.DataFrame):
        df = df_comentarios.copy()
        texts = df["texto"].fillna("").tolist()
        embeddings = self._get_embeddings(texts)

        print("Reduciendo dimensiones y agrupando con HDBSCAN...")
        pca = PCA(n_components=5, random_state=42)
        reduced_embeddings = pca.fit_transform(embeddings)

        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=150,
            metric='euclidean',
            cluster_selection_method='eom',
            core_dist_n_jobs=-1,
            algorithm='boruvka_kdtree'
        )
        labels = clusterer.fit_predict(reduced_embeddings)

        df["id_narrativa"] = [f"n_{l:02d}" if l != -1 else "-1" for l in labels]
        df["postura"] = df["id_narrativa"].apply(
            lambda x: "ruido" if x == "-1" else "apoya"
        )

        # Generar DataFrame de narrativas
        narrativas_list = []
        unique_clusters = set(labels) - {-1}
        
        for cluster_id in sorted(list(unique_clusters)):
            nid = f"n_{cluster_id:02d}"
            sub_df = df[df["id_narrativa"] == nid]
            
            fecha_origen = pd.to_datetime(sub_df["fecha"]).min()
            
            tfidf = TfidfVectorizer(max_features=5, stop_words=None)
            try:
                tfidf.fit(sub_df["texto"].fillna(""))
                kw = ", ".join(tfidf.get_feature_names_out())
            except Exception:
                kw = "general, discusion, opinion"

            narrativas_list.append({
                "id_narrativa": nid,
                "titulo": f"Narrativa {cluster_id + 1}: {kw.split(',')[0].strip().capitalize()}",
                "frases_clave": kw,
                "fecha_origen": str(fecha_origen)
            })

        df_narrativas = pd.DataFrame(narrativas_list)
        return df, df_narrativas