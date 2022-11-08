FROM python:3.8-slim
RUN apt update && apt -y install libpq-dev gcc libczmq-dev librdkafka-dev git

ARG JFROG_BOT_USERNAME
ARG JFROG_BOT_PASS
ARG VERSION

RUN pip config set global.index-url https://$JFROG_BOT_USERNAME:$JFROG_BOT_PASS@splight.jfrog.io/artifactory/api/pypi/splight/simple
COPY requirements.txt requirements.txt
RUN pip install splight-cli==$VERSION && \
    pip install -r requirements.txt

WORKDIR /code
RUN mkdir /code/.config; cp -R /root/.config/pip /code/.config/pip
COPY runner.py  /code
