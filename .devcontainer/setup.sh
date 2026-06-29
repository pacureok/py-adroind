#!/bin/bash
echo "Preparando entorno para Py-Android..."
# Instalar dependencias necesarias para compilar Android
sudo apt-get update && sudo apt-get install -y openjdk-17-jdk unzip
# Crear la carpeta de módulos si no existe
mkdir -p module
echo "Entorno listo. Puedes instalar la librería con: pip install -e ."