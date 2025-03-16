FROM python:3.8.18-alpine

COPY scripts/script.sh ./
COPY scripts/requierements.txt ./

RUN apk add --no-cache git zip

RUN sh script.sh

WORKDIR /home/

RUN mkdir shared

# COPY shared/series_status.json ./shared
COPY main.py ./
COPY src/ ./src
COPY .env ./


ENTRYPOINT ["python3", "./main.py"]