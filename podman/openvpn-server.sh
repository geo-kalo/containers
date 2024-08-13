export EASYRSA_BATCH=1
export EASYRSA='/etc/openvpn/easy-rsa'
sh /etc/openvpn/easy-rsa/easyrsa init-pki 
sh /etc/openvpn/easy-rsa/easyrsa build-ca nopass 
sh /etc/openvpn/easy-rsa/easyrsa gen-req openvpnserver nopass
sh /etc/openvpn/easy-rsa/easyrsa gen-dh
sh /etc/openvpn/easy-rsa/easyrsa sign-req server openvpnserver
cp /etc/openvpn/easy-rsa/pki/dh.pem /etc/openvpn/easy-rsa/pki/ca.crt /etc/openvpn/easy-rsa/pki/issued/openvpnserver.crt /etc/openvpn/easy-rsa/pki/private/openvpnserver.key /etc/openvpn/

sh /etc/openvpn/easy-rsa/easyrsa gen-req myclient1 nopass
sh /etc/openvpn/easy-rsa/easyrsa sign-req client myclient1
sh /etc/openvpn/easy-rsa/easyrsa gen-req myclient2 nopass
sh /etc/openvpn/easy-rsa/easyrsa sign-req client myclient2
sh /etc/openvpn/easy-rsa/easyrsa gen-req myclient3 nopass
sh /etc/openvpn/easy-rsa/easyrsa sign-req client myclient3


cp /etc/openvpn/easy-rsa/pki/private/myclient1.key /mykeys
cp /etc/openvpn/easy-rsa/pki/issued/myclient1.crt  /mykeys
cp /etc/openvpn/easy-rsa/pki/private/myclient2.key /mykeys
cp /etc/openvpn/easy-rsa/pki/issued/myclient2.crt  /mykeys
cp /etc/openvpn/easy-rsa/pki/private/myclient3.key /mykeys
cp /etc/openvpn/easy-rsa/pki/issued/myclient3.crt  /mykeys




cp /etc/openvpn/ca.crt /mykeys
cp /etc/openvpn/ta.key /mykeys

#iptables -t nat -A POSTROUTING -o eth1 -j MASQUERADE


a2enmod ssl
#openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/apache.key -out /etc/ssl/certs/apache.crt
openssl req -new -newkey rsa:4096 -days 365 -nodes -x509  -subj "/C=GR/ST=George/L=Kalogeropoulos/O=Dis/CN=www.fastapi.com" -keyout /etc/ssl/private/apache.key -out /etc/ssl/certs/apache.crt

mkdir -p /var/www/fastapi/doc
mv /main.py /var/www/fastapi/doc/


/activate_virtual_env.sh
/usr/sbin/openvpn --config /etc/openvpn/openvpn.conf &
/etc/init.d/apache2 start 
tail -f /dev/null
