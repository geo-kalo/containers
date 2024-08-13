from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('/workdir/templates'))
template = env.get_template('grafana-provision-v2.jinja')
# output = template.render()

with open("/workdir/token", 'r') as myfile:
    token = myfile.read().strip()

#with open("/workdir/org", 'r') as myfile:
#    id = myfile.read().strip()

output = template.render(token=token, orgId=id)
#print(output)

with open("/workdir/renders/grafana-provision-v2.yaml", 'w') as myfile:
    myfile.write(output)

