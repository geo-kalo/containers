#!/bin/bash
cp  /connection_info/telegraf.conf /etc/telegraf/telegraf.conf
#cp /connection_info/*  /workdir/
#chmod u+x /activate_virtual_env.sh
#/activate_virtual_env.sh
#cp /workdir/renders/telegraf.conf /etc/telegraf/telegraf.conf

#tail -f /dev/null
/entrypoint.sh telegraf
