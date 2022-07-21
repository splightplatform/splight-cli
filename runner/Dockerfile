FROM python:3.8-slim
RUN apt update && apt -y install libpq-dev gcc libczmq-dev librdkafka-dev

ARG JFROG_BOT_USERNAME
ARG JFROG_BOT_PASS

RUN pip config set global.index-url https://$JFROG_BOT_USERNAME:$JFROG_BOT_PASS@splight.jfrog.io/artifactory/api/pypi/splight/simple
RUN pip install splight-cli==0.1.7

WORKDIR /code
RUN mkdir /code/.config; cp -R /root/.config/pip /code/.config/pip
COPY runner.py  /code
# TODO add this stuff in particular images
RUN pip install xgboost