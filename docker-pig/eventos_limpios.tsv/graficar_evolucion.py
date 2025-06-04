import pandas as pd
import matplotlib.pyplot as plt
import os

# Ruta de tu archivo con datos limpios
FILE_PATH = "part-r-00000"

# Leer datos, suponiendo formato TSV con columnas (puedes ajustar si no)
df = pd.read_csv(FILE_PATH, sep="\t", header=None,
                 names=["comuna", "tipo_incidente", "pubMillis", "descripcion", "campo_vacio", "lat", "lon", "uuid"])
df = df.drop(columns=["campo_vacio"])

# Convertir timestamp a fecha (solo fecha, sin hora)
df["fecha"] = pd.to_datetime(df["pubMillis"], unit="ms").dt.date

# Contar eventos por día
conteo_por_dia = df.groupby("fecha").size().reset_index(name="total_incidentes")

# Convertir a datetime para poder graficar fechas
conteo_por_dia["fecha"] = pd.to_datetime(conteo_por_dia["fecha"])

# Seleccionar solo los días que quieres mostrar (los 4 días pico)
dias_pico = ["2025-05-30", "2025-05-31", "2025-06-01", "2025-06-02"]
dias_pico = pd.to_datetime(dias_pico)

# Filtrar el dataframe solo para esos días
df_pico = conteo_por_dia[conteo_por_dia["fecha"].isin(dias_pico)]

# Ordenar por fecha descendente (para que queden en el orden que pediste)
df_pico = df_pico.sort_values("fecha", ascending=False)

# Crear carpeta para guardar el gráfico
os.makedirs("graficos3", exist_ok=True)

# Graficar
plt.figure(figsize=(8, 5))
plt.plot(df_pico["fecha"], df_pico["total_incidentes"], "o-", color="blue", label="Incidentes por día")

# Poner etiquetas con la cantidad justo encima de cada punto
for idx, row in df_pico.iterrows():
    plt.text(row["fecha"], row["total_incidentes"] + max(df_pico["total_incidentes"]) * 0.02, 
             f'{row["total_incidentes"]}', ha='center', fontsize=9, color='blue', fontweight='bold')

# Configurar eje X para mostrar solo esas 4 fechas, en orden inverso (tal como pediste)
plt.xticks(df_pico["fecha"], [d.strftime("%Y-%m-%d") for d in df_pico["fecha"]], rotation=45)

plt.title("Incidentes registrados en días pico")
plt.xlabel("Fecha")
plt.ylabel("Número de incidentes")
plt.grid(True)
plt.tight_layout()

plt.savefig("graficos3/evolucion_incidentes_pico.png", dpi=300)
plt.show()
