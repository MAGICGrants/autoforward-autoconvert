FROM python:3.12-alpine

RUN apk add --no-cache build-base musl-dev gcc
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src src
