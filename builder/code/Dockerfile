ARG RUNNER_IMAGE
FROM $RUNNER_IMAGE
COPY configure.py configure.py

ARG CONFIGURE_SPEC
RUN python configure.py -c "$CONFIGURE_SPEC"