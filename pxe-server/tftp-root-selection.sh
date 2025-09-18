#!/usr/bin/sh

md5_to_test_1=$(md5sum /etc/dnsmasq.conf | cut -d " " -f1)


while true
do
        sleep 5
	md5_to_test_current=$(md5sum /etc/dnsmasq.conf | cut -d " " -f1)
   	if [ "$md5_to_test_1" != "$md5_to_test_current" ]; then
		echo "changed"
                /etc/init.d/dnsmasq restart 
                #md5_to_test_current=$(md5sum /etc/dnsmasq.conf | cut -d " " -f1)
                md5_to_test_1=$md5_to_test_current
        fi

	sleep 5
done

