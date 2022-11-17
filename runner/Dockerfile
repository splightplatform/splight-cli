FROM python:3.8-slim
RUN apt update && apt -y install libpq-dev gcc libczmq-dev librdkafka-dev git

ARG VERSION

COPY requirements.txt requirements.txt
RUN pip install splight-cli==$VERSION && \
    pip install -r requirements.txt

WORKDIR /code
COPY runner.py  /code
