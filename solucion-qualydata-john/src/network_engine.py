import pandas as pd
import networkx as nx

class NetworkEngine:
    def process(self, df_comentarios: pd.DataFrame, time_window_seconds=300):
        print("Buscando patrones de coordinación temporal en el grafo...")
        df = df_comentarios.copy()
        fechas_dt = pd.to_datetime(df["fecha"], utc=True)
        # Convertir a segundos Unix (float) para evitar errores con numpy.timedelta64
        df["ts"] = (fechas_dt - pd.Timestamp("1970-01-01", tz="UTC")) / pd.Timedelta("1s")
        df = df.sort_values("ts")

        G = nx.Graph()

        # Agrupar por publicación
        grouped = df.groupby("publicacion_id")
        for pub_id, group in grouped:
            cuentas = group["cuenta_id"].values
            tiempos = group["ts"].values
            
            n = len(group)
            if n < 2:
                continue

            for i in range(n):
                for j in range(i + 1, n):
                    diff = tiempos[j] - tiempos[i]
                    if diff > time_window_seconds:
                        break
                    
                    c1, c2 = cuentas[i], cuentas[j]
                    if c1 != c2:
                        if G.has_edge(c1, c2):
                            G[c1][c2]["weight"] += 1
                        else:
                            G.add_edge(c1, c2, weight=1)

        # Filtrar conexiones débiles (requiere al menos 3 coincidencias de ráfaga)
        edges_to_remove = [(u, v) for u, v, d in G.edges(data=True) if d["weight"] < 3]
        G.remove_edges_from(edges_to_remove)

        # Agrupar componentes (operaciones de bots/coordinación)
        print("Identificando operaciones de cuentas coordinadas...")
        components = list(nx.connected_components(G))
        
        account_to_op = {}
        for idx, comp in enumerate(components):
            if len(comp) >= 3:  # Solo grupos de 3 o más cuentas
                op_id = f"op_{idx+1:03d}"
                for acc in comp:
                    account_to_op[acc] = op_id

        all_accounts = pd.DataFrame({"cuenta_id": df_comentarios["cuenta_id"].unique()})
        all_accounts["id_operacion"] = all_accounts["cuenta_id"].map(account_to_op).fillna("")
        
        # Renombrar columna para el formato de entrega
        all_accounts = all_accounts.rename(columns={"cuenta_id": "id_cuenta"})
        return all_accounts