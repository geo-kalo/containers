#!/usr/bin/env python
from jinja2 import Environment, FileSystemLoader


env = Environment(loader=FileSystemLoader('/workdir/templates'))
template = env.get_template('docker_telegraf.jinja')
# output = template.render()

with open("/workdir/token", 'r') as myfile:
    token = myfile.read().strip()

#with open("/workdir/org", 'r') as myfile:
#    id = myfile.read().strip()

output = template.render(token=token)
#print(output)

with open("/workdir/renders/telegraf.conf", 'w') as myfile:
    myfile.write(output)

