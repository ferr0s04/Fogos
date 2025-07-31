FROM python:3.11-slim

WORKDIR /app

# Instala o supercronic
ADD https://github.com/aptible/supercronic/releases/download/v0.2.29/supercronic-linux-amd64 /usr/local/bin/supercronic
RUN chmod +x /usr/local/bin/supercronic

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copia cronjob
COPY cronjob /app/cronjob

# Entry point: roda o supercronic
CMD ["/usr/local/bin/supercronic", "/app/cronjob"]
