FROM tiangolo/uvicorn-gunicorn:python3.10

ARG DB_CONNECTION
ARG MODE

ENV SQLALCHEMY_DATABASE_URI=${DB_CONNECTION}
ENV MODE=${MODE}

COPY ./requirements/base.txt .
RUN pip install -r base.txt

COPY ./scripts /app
COPY ./pictures2pages_v2 /app
WORKDIR /app
