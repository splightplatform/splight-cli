FROM python:3.8-slim
RUN apt update && apt -y install libpq-dev gcc libczmq-dev librdkafka-dev

ARG JFROG_BOT_USERNAME
ARG JFROG_BOT_PASS

RUN pip config set global.index-url https://$JFROG_BOT_USERNAME:$JFROG_BOT_PASS@splight.jfrog.io/artifactory/api/pypi/splight/simple
RUN pip install splight-hub==0.1.1

WORKDIR /code
RUN mkdir /code/.config; cp -R /root/.config/pip /code/.config/pip
RUN mkdir /code/.splight
RUN echo "${{ secrets.INTEGRATION_BOT_HUB_ACCESS_ID }}" >> /code/.splight/hub.conf
RUN echo "${{ secrets.INTEGRATION_BOT_HUB_SECRET_KEY }}" >> /code/.splight/hub.conf
RUN echo "https://integrationhub.splight-ae.com" >> /code/.splight/hub.conf
COPY runner.py  /code