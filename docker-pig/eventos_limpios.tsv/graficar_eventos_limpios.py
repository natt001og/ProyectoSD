import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Leer archivo TSV
df = pd.read_csv("part-r-00000", sep="\t", header=None, names=["comuna", "tipo_incidente", "pubMillis", "descripcion", "lat", "lon", "uuid"])

# Convertir pubMillis a fecha
df["fecha"] = pd.to_datetime(df["pubMillis"], unit="ms")
df["dia"] = df["fecha"].dt.date  # solo fecha, sin hora

# Crear carpeta de salida
os.makedirs("graficos", exist_ok=True)

# 1. Incidentes por comuna y tipo
conteo_comuna_tipo = df.groupby(["comuna", "tipo_incidente"]).size().unstack(fill_value=0)
conteo_comuna_tipo.plot(kind="bar", stacked=True, figsize=(10, 6), colormap="tab20")
plt.title("Cantidad de incidentes por comuna y tipo")
plt.ylabel("Cantidad")
plt.xlabel("Comuna")
plt.xticks(rotation=45)
plt.tight_layout()
plt.legend(title="Tipo de incidente")
plt.savefig("graficos/incidentes_comuna_tipo.png")
plt.clf()

# 2. Evolución temporal (por día)
conteo_por_dia = df.groupby("dia").size()
conteo_por_dia.plot(kind="line", marker="o", figsize=(10, 5), color="teal")
plt.title("Evolución diaria de incidentes")
plt.xlabel("Fecha")
plt.ylabel("Cantidad de incidentes")
plt.grid(True)
plt.tight_layout()
plt.savefig("graficos/evolucion_diaria_incidentes.png")
plt.clf()

# 3. Ranking total por comuna
ranking_comunas = df["comuna"].value_counts()
ranking_comunas.plot(kind="bar", figsize=(9, 5), color="tomato")
plt.title("Ranking de incidentes por comuna")
plt.ylabel("Cantidad de incidentes")
plt.xlabel("Comuna")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("graficos/ranking_comunas.png")
plt.clf()

print("Gráficos guardados en la carpeta 'graficos/'")
