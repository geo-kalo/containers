export EASYRSA_BATCH=1
a2enmod ssl

openssl req -new -newkey rsa:4096 -days 365 -nodes -x509  -subj "/C=GR/ST=George/L=Kalogeropoulos/O=Dis/CN=www.fastapi.com" -keyout /etc/ssl/private/api.key -out /etc/ssl/certs/api.crt


mkdir -p /var/lib/misc
chmod 777 /var/lib/misc
#chown dnsmasq:dnsmasq /var/lib/misc


/etc/init.d/dnsmasq start  
chmod 777 /var/lib/misc/dnsmasq.leases
/activate_virtual_env.sh
/etc/init.d/apache2 start



sh  /tftp-root-selection.sh
