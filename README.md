# Entrega Proyecto Parte 1 Sistemas Distribuídos 🚗📊

## Importante 
Actualmente te encuentras en nuestra rama main donde armamos el codigo principal.
Sin embargo, en honor a los distintos tipos de cache implementados con sus respectivos distintos generadores de tráfico, se crearon 4 ramas en total: 

rama_cacheP1: Sistema de remoción del cache -> LRU - 50mb
              Distribucíon generador de tráfico -> Poisson
rama_cacheP2: Sistema de remoción del cache -> LFU - 100mb
              Distribucíon generador de tráfico -> Poisson
rama_cacheZ1: Sistema de remoción del cache -> LRU - 50mb
              Distribucíon generador de tráfico -> Zipf
rama_cacheP1: Sistema de remoción del cache -> LFU - 100mb
              Distribucíon generador de tráfico -> Zipf

Cada una de estas ramas tiene exactamente la misma estructura, solo se hicieron los cambios correpondientes en docker-compose.yml para el tipo de cache y tamaño, y los cambios correspondientes en gdt.py para el tipo de distribución seguida por el generador de tráfico.

## Arquitectura General

El sistema consta de los siguientes componentes:

- **Scraper**: Obtiene eventos de tráfico (como accidentes, atascos, etc.) desde la API pública del mapa en vivo de Waze. Guarda los eventos únicos en MongoDB.
- **Base de Datos (MongoDB)**: Almacena de manera persistente los eventos capturados por el scraper.
- **Caché (Flask + Redis)**: Expone una API REST para consultar eventos por UUID y guarda resultados temporalmente para acelerar accesos repetidos.
- **Generador de Tráfico**: Simula consultas concurrentes al sistema usando distribuciones probabilísticas (por ejemplo, Poisson), evaluando el comportamiento de la caché y la base de datos.
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

El scraper se ejecutará y guardará los datos en formato JSON en el contenedor como volumen para que se mantengan guardados.
Se levvantaran todos los contenedores y se realizaran consultas en seguida al sistema.

## 📂 Estructura del proyecto
```bash
.
├── scraper/              # Scraper de eventos desde Waze
│   └── scraper.py
    └── Dockerfile
    └── requirements.txt
├── cache/                # Servidor Flask + Redis como caché
│   └── cache.py
    └── Dockerfile
├── generador_trafico/    # Simula tráfico usando distribución de Poisson
│   └── generador.py
    └── Dockerfile
├── docker-compose.yml    # Orquestación de contenedores
└── README.md             # Este archivo

```
## 🛠 Tecnologías utilizadas

    Python (scraping, servidor REST, generación de tráfico)

    MongoDB (almacenamiento persistente)

    Redis (sistema de caché con TTL parametrizable)

    Flask (API REST para interacción entre módulos)

    Docker & Docker Compose (despliegue modular)

## Estado actual

✔ Scraper funcional conectado a MongoDB
✔ API REST con caché y TTL configurable
✔ Generador de carga que simula tráfico realista
✔ Sistema completamente containerizado
✔ Documentación técnica en LaTeX incluida

## 📌 Notas

- El scraping solo obtiene datos visibles en el mapa en vivo al momento de ejecución.
- La base de datos aun no esta subida de forma remota a mongo, solo la manejamos de forma local

## Autoras 

Isidora Gonzalez
Natalia Ortega


