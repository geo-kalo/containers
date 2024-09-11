#!/usr/bin/bash
#
#

echo 'nameserver 8.8.8.8' >> /etc/resolv.conf
iptables-restore < /iptables-rules

ulogd -d

default_interface=$(route -n | grep 10.0.48 | awk '{print $8}')
while true; do
	default_route=$(ip route show default | awk '{print $3}')
	if [ "$default_route" != "10.0.48.1" ]; then
		ip route replace default via 10.0.48.1 dev $default_interface
	fi
	sleep 10
done
