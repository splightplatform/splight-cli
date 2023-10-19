ARG RUNNER_IMAGE
FROM $RUNNER_IMAGE
COPY /configure/ /configure/
WORKDIR /configure/

ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG S3_BUCKET_NAME

RUN pip install -r configure_requirements.txt
ARG CONFIGURE_SPEC
RUN python3 configure.py -c "$CONFIGURE_SPEC"
