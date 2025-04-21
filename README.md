# Entrega Proyecto Parte 1 Sistemas Distribuídos 🚗📊

##  Requisitos

- Docker
- Docker Compose
- Git

## 🚀 Ejecución del Scraper

Para ejecutar el scraper localmente en un contenedor Docker:

```bash
# Clona el repositorio
git clone https://github.com/tu-usuario/tu-repo.git
cd tu-repo

# Ejecuta el scraper con Docker Compose o si quieres volver a ejecutarlo tras haber hecho cambios
sudo docker-compose up --build

# Si se quiere ejecutar otra vez sin haber hecho cambios en el codigo
sudo docker-compose up


```

El scraper se ejecutará y guardará los datos en formato JSON en el contenedor (puedes modificarlo para guardar en volumen compartido o base de datos en el futuro).


## 📌 Notas

- El scraping solo obtiene datos visibles en el mapa en vivo al momento de ejecución.
- El script aún no está programado para ejecución periódica automática (cron o similar).


