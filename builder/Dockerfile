ARG RUNNER_IMAGE
FROM $RUNNER_IMAGE
COPY configure.py configure.py

ARG CONFIGURE_SPEC
RUN pip install splight-cli==${SPLIGHT_CLI_VERSION}
RUN python configure.py -c "$CONFIGURE_SPEC"
