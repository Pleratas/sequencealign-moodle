FROM bitnamilegacy/moodle:latest

USER root

# Install Python for the sequence alignment backend.
RUN install_packages python3 && \
    ln -sf /usr/bin/python3 /usr/bin/python

# Copy the Moodle plugin into the Moodle local plugins directory.
COPY --chown=1001:0 local/sequencealign /opt/bitnami/moodle/local/sequencealign

USER 1001