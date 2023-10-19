ARG RUNNER_IMAGE
FROM $RUNNER_IMAGE
COPY configure.py configure.py
COPY install_requirements.py install_requirements.py

ENV AWS_ACCESS_KEY_ID=
ENV AWS_SECRET_ACCESS_KEY=

RUN pip install boto3
RUN pip install py7zr
RUN pip install typing
ARG CONFIGURE_SPEC
RUN python3 configure.py -c "$CONFIGURE_SPEC"
