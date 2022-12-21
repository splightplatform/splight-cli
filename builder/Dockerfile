FROM 609067598877.dkr.ecr.us-east-1.amazonaws.com/splight-jobs:builder-base

RUN apk update && \
    apk add \
    python3 \
    py3-pip \
    python3-dev \
    curl \
    unzip \
    libpq-dev \
    gcc \
    build-base \
    git


ARG GITHUB_TOKEN
COPY requirements.txt requirements.txt
RUN GITHUB_TOKEN=${GITHUB_TOKEN} pip install -r requirements.txt

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip awscliv2.zip && ./aws/install --update

ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY

ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}

RUN mkdir -p /code
WORKDIR /code

COPY ./code /code
