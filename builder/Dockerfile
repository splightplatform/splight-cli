FROM --platform=linux/amd64 ubuntu:20.04
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python3 libpq-dev python3-dev pip curl unzip docker.io build-essential

ARG JFROG_BOT_USERNAME
ARG JFROG_BOT_PASS

RUN pip config set global.index-url https://$JFROG_BOT_USERNAME:$JFROG_BOT_PASS@splight.jfrog.io/artifactory/api/pypi/splight/simple
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip awscliv2.zip && ./aws/install
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
# RUN aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 609067598877.dkr.ecr.us-east-1.amazonaws.com
RUN docker login -u AWS -p $(aws ecr get-login-password --region us-east-1) 609067598877.dkr.ecr.us-east-1.amazonaws.com

RUN mkdir -p /code
WORKDIR /code

COPY ./code /code