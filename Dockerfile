# Usar uma imagem Python oficial
FROM python:3.12-slim

# Definir o diretório de trabalho
WORKDIR /app

# Copiar os arquivos do script para o contêiner
COPY . /app

# Instalar as dependências
# RUN pip install speedtest-cli mysql-connector-python

RUN pip install poetry

RUN poetry install

# Comando para executar o script
CMD poetry run python speed_test.py
