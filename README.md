# Entrega Proyecto Parte 1 Sistemas Distribuidos 🚗📊

## Importante 
Actualmente te encuentras en nuestra rama main en donde se armó el código principal.
Sin embargo, en honor a los distintos tipos de caché implementados con sus respectivos distintos generadores de tráfico, se crearon 4 ramas en total: 

rama_cacheP1: Sistema de remoción del cache -> LRU - 50mb
              Distribución generador de tráfico -> Poisson
              
rama_cacheP2: Sistema de remoción del cache -> LFU - 100mb
              Distribución generador de tráfico -> Poisson
              
rama_cacheZ1: Sistema de remoción del cache -> LRU - 50mb
              Distribución generador de tráfico -> Zipf
              
rama_cacheP1: Sistema de remoción del cache -> LFU - 100mb
              Distribución generador de tráfico -> Zipf

Cada una de estas ramas tiene exactamente la misma estructura, sólo se hicieron los cambios correpondientes en docker-compose.yml para el tipo de caché y tamaño y los cambios correspondientes en gdt.py para el tipo de distribución seguida por el generador de tráfico.

## Arquitectura General

El sistema consta de los siguientes componentes:

- **Scraper**: Obtiene eventos de tráfico (como accidentes, atascos, etc.) desde la API pública del mapa en vivo de Waze. Guarda los eventos únicos en MongoDB.
- **Base de Datos (MongoDB)**: Almacena de manera persistente los eventos capturados por el Scraper.
- **Caché (Flask + Redis)**: Expone una API REST para consultar eventos por UUID y guarda resultados temporalmente para acelerar accesos repetidos.
- **Generador de Tráfico**: Simula consultas concurrentes al sistema usando distribuciones probabilísticas (por ejemplo, Poisson), evaluando el comportamiento de la caché y la base de datos.
- **Filtrado y Procesamiento (Apache Pig)**: Procesa los datos recolectados, aplicando transformaciones, limpieza y agregaciones, todo ejecutado dentro de un contenedor Docker que simula un entorno Hadoop local.
- **Docker Compose**: Orquesta el despliegue de todos los servicios en contenedores separados, facilitando su ejecución conjunta.

---

##  Requisitos

- Docker
- Docker Compose
- Git

## 🚀 Ejecución del sistema

1. Clona el repositorio

```bash
# Clona el repositorio
git clone https://github.com/tu-usuario/ProyectoSD.git.
cd ProyectoSD

# Levanta los servicios con Docker
sudo docker-compose up --build

# Si se quiere ejecutar otra vez sin haber hecho cambios en el codigo
sudo docker-compose up


```

## Sobre la ejecución del procesamiento y filtrado de datos 

```bash

docker-compose build pig  # esto es para crear la imagen de pig
docker-compose up -d pig # iniciar el contenedor
docker exec -it pig bash # acceder al contenedor

#ejecución de los sprits
pig -x local homogeneizacion.pig 
pig -x local procesamiento.pig

```

El scraper se ejecutará y guardará los datos en formato JSON en el contenedor como volumen para que se mantengan guardados.
Se levvantarán todos los contenedores y se realizarán consultas en seguida al sistema.

## 📂 Estructura del proyecto
```bash
.
├── scraper/              # Scraper de eventos desde Waze
│   ├── scraper.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── cache/                # Servidor Flask + Redis como caché
│   ├── cache.py
│   └── Dockerfile
│
├── generador_trafico/    # Simula tráfico usando distintas distribuciones
│   ├── generador.py
│   └── Dockerfile
│
├── docker-pig/           # Módulo de filtrado y análisis con Apache Pig
│   ├── Dockerfile        # Imagen personalizada de Apache Pig
│   ├── data.tsv          # Datos crudos de eventos
│   ├── Filtrado.pig
│   └── procesamiento.pig
│
├── docker-compose.yml    # Orquestación de todos los contenedores
└── README.md             # Este archivo

```
## 🛠 Tecnologías utilizadas

Python (scraping, servidor REST, generación de tráfico)

MongoDB (almacenamiento)

Redis (caché con políticas LRU/LFU)

Flask (API REST)

Apache Pig (procesamiento tipo MapReduce)

Hadoop (modo local para Pig)

Docker & Docker Compose (contenedorización y despliegue)

## Estado actual

✔ Scraper funcional conectado a MongoDB
✔ API REST con caché y TTL configurable
✔ Generador de carga que simula tráfico realista
✔ Sistema completamente containerizado
✔ Documentación técnica en LaTeX incluida

## 📌 Notas

- El scraping solo obtiene datos visibles en el mapa en vivo al momento de ejecución.
- La base de datos aún no esta subida de forma remota a Mongo, sólo la manejamos de forma local.

## Autoras 

Isidora González
Natalia Ortega


