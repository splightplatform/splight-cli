ARG RUNNER_IMAGE
FROM $RUNNER_IMAGE
COPY configure.py configure.py
COPY manager.py manager.py
COPY configure_requirements.txt configure_requirements.txt

ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY

RUN pip install -r configure_requirements.txt
ARG CONFIGURE_SPEC
RUN python3 configure.py -c "$CONFIGURE_SPEC"
