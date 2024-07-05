# syntax=docker/dockerfile:1
FROM --platform=linux/amd64 python:3.11.7-slim

WORKDIR /whl
RUN pip install --upgrade splight-runner

ARG SPL_PACKAGE
ARG SPL_PACKAGE_VERSION
RUN pip install ${SPL_PACKAGE}==${SPL_PACKAGE_VERSION}

ARG COMPONENT_NAME
ARG COMPONENT_VERSION

WORKDIR /app
COPY . .
RUN python installer.py --name ${COMPONENT_NAME} --version ${COMPONENT_VERSION}

# Cleaning up files
RUN rm installer.py Dockerfile

ENTRYPOINT ["splight-runner", "run-component"]
