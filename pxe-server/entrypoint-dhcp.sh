export EASYRSA_BATCH=1
a2enmod ssl

openssl req -new -newkey rsa:4096 -days 365 -nodes -x509  -subj "/C=GR/ST=George/L=Kalogeropoulos/O=Dis/CN=www.fastapi.com" -keyout /etc/ssl/private/api.key -out /etc/ssl/certs/api.crt


mkdir -p /var/lib/misc
chmod 777 /var/lib/misc
#chown dnsmasq:dnsmasq /var/lib/misc


#mkdir  /srv/tftp-win/boot
#mkdir  /srv/tftp-win/sources
#cp /srv/nfs/win-install/bootmgr        /srv/tftp-win/
#cp /srv/nfs/win-install/bootmgr.efi    /srv/tftp-win/
#cp /srv/nfs/win-install/boot/boot.sdi  /srv/tftp-win/boot/
#cp /srv/nfs/win-install/sources/boot.wim /srv/tftp-win/sources/
#cp /srv/tftp-debian/debian-installer/amd64/pxelinux.0  /srv/tftp-win/
#cp /usr/lib/syslinux/modules/bios/ldlinux.c32 	/srv/tftp-win/
#cp /usr/lib/syslinux/modules/bios/menu.c32 	/srv/tftp-win/
#cp /usr/lib/syslinux/modules/bios/libutil.c32   /srv/tftp-win

#mkdir /srv/tftp-win/pxelinux.cfg
#cp /tmp/default  /srv/tftp-win/pxelinux.cfg/
#wimlib-imagex mount /srv/nfs/win-install/sources/boot.wim 1  /srv/winpe-creation 
#wimlib-imagex mount /srv/tftp-win/sources/boot.wim 1 /srv/winpe-creation --read-write
#echo -e "wpeinit\nnet use Z: \\\\192.168.199.1\\win-install\nZ:\\setup.exe /unattend:Z:\\unattend.xml" > /srv/winpe-creation/Windows/System32/startnet.cmd
#wimlib-imagex unmount /srv/winpe-creation --commit
hostname  container-web-dnsmasq

#cp -r /srv/nfs/win-install/tftp-win /srv 



/etc/init.d/dnsmasq start  
chmod 777 /var/lib/misc/dnsmasq.leases
/activate_virtual_env.sh
/etc/init.d/apache2 start
/etc/init.d/smbd start



sh  /tftp-root-selection.sh
