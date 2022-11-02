FROM docker:20.10.21-cli

RUN apk update && \
    apk add \
    python3 \
    py3-pip \
    python3-dev \
    curl \
    unzip \
    libpq-dev \
    gcc \
    build-base


ARG JFROG_BOT_USERNAME
ARG JFROG_BOT_PASS

RUN pip config set global.index-url https://$JFROG_BOT_USERNAME:$JFROG_BOT_PASS@splight.jfrog.io/artifactory/api/pypi/splight/simple

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip awscliv2.zip && ./aws/install

ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY

ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}


RUN mkdir -p /code
WORKDIR /code

COPY ./code /code