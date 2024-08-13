FROM grafana/grafana:latest

USER root

ENV GF_SECURITY_ADMIN_USER=admin \
    GF_SECURITY_ADMIN_PASSWORD=12345678 \
    GF_LOG_MODE=file

RUN mkdir /connection_info \
    && mkdir -p /workdir/templates \
    && mkdir -p /workdir/renders \
    && touch /workdir/renders/grafana-provision-v2.yaml \
    && touch /workdir/renders/telegraf.conf
    

RUN apk update \
    && apk add --no-cache python3 \
    && mkdir /venv

VOLUME /connection_info

COPY activate_virtual_env.sh /activate_virtual_env.sh
COPY test.py /workdir/file_generator.py
COPY telegrap_generator.py /workdir/file_generator_teletegraf.py

COPY grafana-provision-v2.jinja /workdir/templates
COPY docker_telegraf.jinja /workdir/templates


COPY grafana_entrypoint.sh /
COPY grafana_dashboard.yml /
COPY fixed.json /dashboard_import.json 


RUN chmod u+x /activate_virtual_env.sh \
    && chmod u+x /grafana_entrypoint.sh

ENTRYPOINT ["/grafana_entrypoint.sh"]

