FROM python:3.11-slim

# instalar ffmpeg
RUN apt-get update && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# diretório da app
WORKDIR /app

# copiar arquivos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# porta do render
EXPOSE 10000

# start
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
