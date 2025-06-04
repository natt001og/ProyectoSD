import pandas as pd
import matplotlib.pyplot as plt
import os

# Leer archivo TSV (local, sin rutas externas)
df = pd.read_csv("part-r-00000", sep="\t", header=None,
                 names=["comuna", "tipo_incidente", "pubMillis", "descripcion", "lat", "lon", "uuid"])

# Convertir pubMillis a fecha
df["fecha"] = pd.to_datetime(df["pubMillis"], unit="ms")
df["dia"] = df["fecha"].dt.date  # solo fecha, sin hora

# Crear carpeta de salida graficos1
output_folder = "graficos1"
os.makedirs(output_folder, exist_ok=True)

# 1. Incidentes por comuna y tipo
conteo_comuna_tipo = df.groupby(["comuna", "tipo_incidente"]).size().unstack(fill_value=0)
plt.figure(figsize=(12, 7))
conteo_comuna_tipo.plot(kind="bar", stacked=True, colormap="tab20", ax=plt.gca())
plt.title("Cantidad de incidentes por comuna y tipo")
plt.ylabel("Cantidad")
plt.xlabel("Comuna")
plt.xticks(rotation=45, ha='right')
plt.legend(title="Tipo de incidente", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "incidentes_comuna_tipo.png"))
plt.clf()

# 3. Ranking total por comuna
ranking_comunas = df["comuna"].value_counts()
plt.figure(figsize=(10, 6))
ranking_comunas.plot(kind="bar", color="tomato")
plt.title("Ranking de incidentes por comuna")
plt.ylabel("Cantidad de incidentes")
plt.xlabel("Comuna")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "ranking_comunas.png"))
plt.clf()

print(f"Gráficos guardados en la carpeta '{output_folder}/'")
