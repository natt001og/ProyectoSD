from pymongo import MongoClient
import pandas as pd

client = MongoClient("mongodb://localhost:27017/")
db = client["trafico"]
collection = db["eventos_limpios"]

print("Exportando colección limpia a TSV para Pig...")

datos = list(collection.find({}, {"_id": 0}))
df = pd.DataFrame(datos)
df.to_csv("eventos_limpios_pig.tsv", sep="\t", index=False)

print("Archivo 'eventos_limpios_pig.tsv' exportado correctamente.")
