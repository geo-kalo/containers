#!/bin/bash
cp /connection_info/*  /workdir/
/activate_virtual_env.sh
#cp /workdir/renders/grafana-provision-v2.yaml /etc/grafana/provisioning/dashboards/
cp /workdir/renders/grafana-provision-v2.yaml /etc/grafana/provisioning/datasources/
mv  /grafana_dashboard.yml /etc/grafana/provisioning/dashboards/
mv  /dashboard_import.json /etc/grafana/provisioning/dashboards/
cp  /workdir/renders/telegraf.conf /connection_info/
/run.sh

