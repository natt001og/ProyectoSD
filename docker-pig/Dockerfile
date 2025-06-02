FROM openjdk:8-jdk-slim

# Descarga e instala Pig 0.17.0
RUN apt-get update && \
    apt-get install -y wget && \
    wget https://archive.apache.org/dist/pig/pig-0.17.0/pig-0.17.0.tar.gz && \
    tar -xzf pig-0.17.0.tar.gz -C /opt && \
    rm pig-0.17.0.tar.gz && \
    ln -s /opt/pig-0.17.0 /opt/pig

ENV PIG_HOME=/opt/pig
ENV PATH=$PATH:$PIG_HOME/bin

WORKDIR /app
