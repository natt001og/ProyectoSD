# Imagen base con Java, necesario para Apache Pig
FROM openjdk:11-jre-slim


# Instalar wget para descargar Pig y tar para descomprimir
RUN apt-get update && apt-get install -y wget tar

# Descargar Apache Pig 0.17.0
RUN wget https://downloads.apache.org/pig/pig-0.17.0/pig-0.17.0.tar.gz

# Descomprimir y mover a /opt/pig
RUN tar -xzf pig-0.17.0.tar.gz && mv pig-0.17.0 /opt/pig && rm pig-0.17.0.tar.gz

# Variables de entorno para Pig
ENV PIG_HOME=/opt/pig
ENV PATH=$PATH:$PIG_HOME/bin

# Directorio de trabajo donde montarás tu proyecto (se usará volumen)
WORKDIR /data

# Comando por defecto: abrir shell de pig
CMD ["pig"]
