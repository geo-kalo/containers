cp /connection_info/*  /workdir/
/activate_virtual_env.sh
#cp /workdir/renders/grafana-provision-v2.yaml /etc/grafana/provisioning/dashboards/
cp /workdir/renders/grafana-provision-v2.yaml /etc/grafana/provisioning/datasources/
/run.sh

