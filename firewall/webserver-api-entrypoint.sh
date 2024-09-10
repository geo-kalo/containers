export EASYRSA_BATCH=1
a2enmod ssl

openssl req -new -newkey rsa:4096 -days 365 -nodes -x509  -subj "/C=GR/ST=George/L=Kalogeropoulos/O=Dis/CN=www.fastapi.com" -keyout /etc/ssl/private/apache.key -out /etc/ssl/certs/apache.crt

mkdir -p /var/www/fastapi/doc
touch /var/www/fastapi/doc/iptables
chmod 777 /var/www/fastapi/doc/iptables
mv /main.py /var/www/fastapi/doc/

/activate_virtual_env.sh
/etc/init.d/apache2 start
tail -f /dev/null

