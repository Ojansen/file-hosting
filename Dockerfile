FROM python:3.12-slim
LABEL authors="obejansen"

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
COPY ./.env /app/.env

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./file-hosting /app/