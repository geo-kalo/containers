from 		docker.io/library/telegraf

run     mkdir /connection_info 
#run     mkdir /connection_info && \
        #mkdir -p /workdir/templates && \
        #mkdir -p /workdir/renders && \
        #touch /workdir/renders/telegraf.conf && \
#        apt update -y && \
#        apt install -y python3.11-venv && \
#        apt install -y python3 && \
#        mkdir /venv

copy 	telegraf_entrypoint.sh  /
run     chmod u+x /telegraf_entrypoint.sh

#copy    activate_virtual_env.sh /
#run     chmod u+x /activate_virtual_env.sh

#copy    telegrap_generator.py   /workdir/file_generator.py
#run 	chmod u+x /workdir/file_generator.py
#copy	docker_telegraf.jinja   /workdir/templates/ 

volume	/var/run/docker.sock
volume  /connection_info
expose	8125

#entrypoint  tail -f /dev/null
entrypoint /telegraf_entrypoint.sh
