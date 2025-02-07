#!/bin/bash

# Atualiza e instala pacotes necessários
sudo apt update && sudo apt install -y unzip python3-pip

# Instala boto3
pip install boto3

# Verifica se o arquivo zip está no mesmo diretório do script
ZIP_FILE="exercise-textract.zip"
if [ ! -f "$ZIP_FILE" ]; then
    echo "Arquivo $ZIP_FILE não encontrado! Certifique-se de que ele está no mesmo diretório do script."
    exit 1
fi

# Descompacta o arquivo zip
unzip "$ZIP_FILE"

# Entra no diretório do exercício
cd exercise-textract || exit

# Executa o script Python
python3 main.py