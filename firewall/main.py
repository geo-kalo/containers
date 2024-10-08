from fastapi import FastAPI, Depends, HTTPException
from a2wsgi import ASGIMiddleware
from sqlalchemy import create_engine  # to thelo gia to create tou object
from sqlalchemy.engine import URL  # to thelo gia to url
from sqlalchemy.exc import OperationalError  # alios den fernei exception
from sqlalchemy.orm import sessionmaker, Session  # gia ta session
from sqlalchemy.ext.declarative import declarative_base  # create tables
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy import insert
from pydantic import BaseModel, validator  # to xriazome kai to validate pou ginete mesa sto class Firewallentry
from fastapi import Depends
import ipaddress
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from datetime import datetime
from sqlalchemy import text, column
from jinja2 import Environment, FileSystemLoader
import subprocess
import socket
import time




app = FastAPI()
application = ASGIMiddleware(app)

# https://jnikenoueba.medium.com/using-fastapi-with-sqlalchemy-5cd370473fe5
# https://medium.com/technology-hits/database-queries-in-python-sqlalchemy-postgresql-e90afe0a06b4
# https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_core_connecting_to_database.htm
# https://www.datacamp.com/tutorial/sqlalchemy-tutorial-examples
# https://jnikenoueba.medium.com/using-fastapi-with-sqlalchemy-5cd370473fe5
# https://serverfault.com/questions/140622/how-can-i-port-forward-with-iptables
#https://hangarau.space/running-and-debugging-iptables-inside-a-docker-container/

Base = declarative_base()

class Firewall(Base):
    __tablename__ = 'firewall'
    rule_id = Column(Integer, primary_key=True, autoincrement=True)
    chain = Column(String(15), nullable=False)  # e.g., INPUT, OUTPUT, FORWARD
    protocol = Column(String(10))  # e.g., tcp, udp, icmp
    src_ip = Column(INET)
    dst_ip = Column(INET)
    src_port = Column(Integer)  # Source Port
    dst_port = Column(Integer)  # Destination Port
    action = Column(String(10), nullable=False)  # e.g., ACCEPT, DROP, REJECT
    in_interface = Column(String(20))  # Incoming network interface
    out_interface = Column(String(20))  # Outgoing network interface
    state = Column(String(20))  # Connection state (e.g., NEW, ESTABLISHED)
    comment = Column(Text)  # Optional comment about the rule
    # log = Column(Boolean, default=False)  # Whether to log the rule
    created_at = Column(DateTime, default=datetime.utcnow)  # Creation timestamp
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last update timestamp
    order_id = Column(Integer) #, server_default=text("rule_id"))
    #order_id = Column(Integer, server_default=text("rule_id"))




def my_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('0.0.0.0', 65431)
    print(f'Starting up on {server_address[0]} port {server_address[1]}')
    sock.bind(server_address)
    sock.listen(1)
    gg = 0
    while True:
        print('Waiting for a connection...')
        connection, client_address = sock.accept()
        try:
            print(f'Connection from {client_address}')
            while True:
                data = connection.recv(2048)
                if data:
                    print(f'Received data: {data.decode("utf-8")}')
                    if "ok" in data.decode("utf-8"):
                        print("Firewall reported ok")
                        gg = 1
                    else:
                        print("Firewall reported not ok")
                        gg = 1
                    break
        finally:
            connection.close()
        if gg == 1:
            break
        time.sleep(10)
        break


class Firewallentry(BaseModel):
    chain: str
    protocol: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    action: str
    in_interface: str
    out_interface: str
    state: str
    comment: str
    order_id: int

    @validator('src_ip', 'dst_ip')
    def validate_ip(cls, v):
        try:
            ipaddress.ip_address(v)
        except ValueError:
            raise ValueError(f"Invalid IP address: {v}")
        return v

# database open / sessions
def create_eng():
    url_object = URL.create(
        "postgresql+psycopg2",
        username="admin",
        password="666",
        host="192.168.199.8",
        database="firewall",
    )
    engine = create_engine(url_object)
    return engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=create_eng())

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
#####################################

@app.post("/create-table/{item}", response_model=None)
async def create_table(item: str):
    try:
        print(item)
        engine = create_eng()
        Base.metadata.create_all(engine)
        return "table created"
    except OperationalError as e:
        print("Connection error due to the following error: \n", str(e.orig))
        return e

@app.post("/insert-rule/", response_model=None)
async def insert_rule(rule: Firewallentry, db: Session = Depends(get_db)):
    try:
        new_rule = Firewall(
            chain=rule.chain,
            protocol=rule.protocol,
            src_ip=rule.src_ip,
            dst_ip=rule.dst_ip,
            src_port=rule.src_port,
            dst_port=rule.dst_port,
            action=rule.action,
            in_interface=rule.in_interface,
            out_interface=rule.out_interface,
            state=rule.state,
            comment=rule.comment,
            order_id=rule.order_id
        )
        db.add(new_rule)
        db.commit()
        db.refresh(new_rule)
        if new_rule.order_id == 0:
            new_rule.order_id = new_rule.rule_id
        else:
            new_rule.order_id = new_rule.order_id
        db.commit()
        return {"message": "Firewall rule added successfully"}
    except OperationalError as e:
        db.rollback()
        print(f"Connection error due to the following error: \n{str(e.orig)}")
        raise HTTPException(status_code=500, detail=f"Connection error: {str(e.orig)}")

@app.get("/get-rule/{rule_id}")
async def get_rule(rule_id: int, db: Session = Depends(get_db)):
    try:
        rule = db.query(Firewall).filter(Firewall.rule_id == rule_id).first()
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        return rule

    except OperationalError as e:
        print(f"Error: {str(e)}")

@app.get("/get-rules")
async def get_rules(db: Session = Depends(get_db)):
    try:
        rules = rules = db.query(Firewall).all()
        if not rules:
            raise HTTPException(status_code=404, detail="Empty database")
        return rules
    except OperationalError as e:
        print(f"Error: {str(e)}")



@app.put("/update-rule/{rule_id}")
async def update_rule(rule_id: int, updated_rule: Firewallentry, db: Session = Depends(get_db)):
    rule = db.query(Firewall).filter(Firewall.rule_id == rule_id).first()

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule.chain = updated_rule.chain
    rule.protocol = updated_rule.protocol
    rule.src_ip = updated_rule.src_ip
    rule.dst_ip = updated_rule.dst_ip
    rule.src_port = updated_rule.src_port
    rule.dst_port = updated_rule.dst_port
    rule.action = updated_rule.action
    rule.in_interface = updated_rule.in_interface
    rule.out_interface = updated_rule.out_interface
    rule.state = updated_rule.state
    rule.comment = updated_rule.comment
    rule.order_id = updated_rule.order_id

    db.commit()
    db.refresh(rule)
    return {"message": "Firewall rule updated successfully", "rule": rule}


@app.post("/delete-rule/{rule_id}")
async def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    try:
        firewall_rule = db.query(Firewall).filter(Firewall.rule_id == rule_id).first()
        if not firewall_rule:
            raise HTTPException(status_code=404, detail="Rule not found")

        db.delete(firewall_rule)
        db.commit()
        return {"message": "Rule deleted successfully"}
    except OperationalError as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Error on delete")


from jinja2 import TemplateError

@app.get("/create-iptables")
async def create_iptables(db: Session = Depends(get_db)):
    try:
        print("Endpoint hit - Starting to process request")
        env = Environment(loader=FileSystemLoader('/var/www/fastapi/doc/'))
        try:
            template = env.get_template('iptables.jinja')
        except TemplateError as e:
            print(f"Template error: {str(e)}")
            raise HTTPException(status_code=500, detail="Template error")

        rules = db.query(Firewall).order_by(Firewall.rule_id.asc()).all()
        if not rules:
            print("No rules found in the database")
            raise HTTPException(status_code=404, detail="Empty database")
        print(f"Number of rules fetched: {len(rules)}")

        l_rules = []
        for rule in rules:
            print(f"Processing rule: {rule.rule_id}")
            d_rule = {
                "rule_id": rule.rule_id,
                "chain": rule.chain,
                "protocol": rule.protocol,
                "src_ip": rule.src_ip,
                "dst_ip": rule.dst_ip,
                "src_port": rule.src_port,
                "dst_port": rule.dst_port,
                "action": rule.action,
                "in_interface": rule.in_interface,
                "out_interface": rule.out_interface,
                "state": rule.state,
                "comment": rule.comment,
                "order_id": rule.order_id
            }
            l_rules.append(d_rule)

        try:
            content = template.render(rules=l_rules)
        except TemplateError as e:
            print(f"Error rendering template: {str(e)}")
            raise HTTPException(status_code=500, detail="Error rendering template")

        print("Template rendered successfully")

        with open("/var/www/fastapi/doc/iptables", 'a') as myfile:
            myfile.write(content)

        try:
            command = 'cat /var/www/fastapi/doc/iptables | nc -q0 192.168.199.2 65432 '
            import_rules = subprocess.run(command, shell=True, capture_output=True, text=True)
            print(import_rules)
            command = 'truncate -s0 /var/www/fastapi/doc/iptables'
            subprocess.run(command, shell=True, capture_output=True, text=True)
            my_socket()
        except Exception as e:
            print(e)

        return {"message": "iptables file created successfully and imported"}


    except OperationalError as e:
        print(f"Database connection error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection error")

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")







# curl -k -X 'POST' https://localhost:49888/insert-rule/   -H 'Content-Type: application/json'   -d '{
#        "chain": "INPUT",
#        "protocol": "tcp",
#        "src_ip": "192.168.1.1",
#        "dst_ip": "192.168.1.2",
#        "src_port": 80,
#        "dst_port": 8080,
#        "action": "ACCEPT",
#        "in_interface": "eth0",
#        "out_interface": "eth1",
#        "state": "NEW",
#        "comment": "Allow HTTP traffic"
#      }'






#curl -k -X PUT "https://127.0.0.1:49888/update-rule/2" \
#    -H "Content-Type: application/json" \
#    -d '{
#        "chain": "OUTPUT",
#        "protocol": "tcp",
#        "src_ip": "20.0.0.20",
#        "dst_ip": "20.0.0.20",
#        "src_port": 80,
#        "dst_port": 443,
#        "action": "ACCEPT",
#        "in_interface": "eth100",
#        "out_interface": "eth1",
#        "comment": "Updated rule"
#    }'



#curl -k -X 'GET' https://localhost:49888/create-iptables -H 'Content-Type: application/json'


#curl -k -X 'POST' https://localhost:49888/create-table/add   -H 'Content-Type: application/json'   -d '"firewall"'

#curl -k -X 'POST' https://localhost:49888/delete-rule/4   -H 'Content-Type: application/json'   -d '"firewall"'




#source /venv/bin/activate



#thelo ena jinja  kai na to kano kai copy sto sosto path


"""
*filter
# Allow all outgoing, but drop incoming and forwarding packets by default
:INPUT DROP [0:0]
:FORWARD DROP [0:0]
:OUTPUT ACCEPT [0:0]

# Custom per-protocol chains
:UDP - [0:0]
:TCP - [0:0]
:ICMP - [0:0]

# Acceptable UDP traffic

# Acceptable TCP traffic
-A TCP -p tcp --dport 22 -j ACCEPT

# Acceptable ICMP traffic

# Boilerplate acceptance policy
-A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
-A INPUT -i lo -j ACCEPT

# Drop invalid packets
-A INPUT -m conntrack --ctstate INVALID -j DROP

# Pass traffic to protocol-specific chains
## Only allow new connections (established and related should already be handled)
## For TCP, additionally only allow new SYN packets since that is the only valid
## method for establishing a new TCP connection
-A INPUT -p udp -m conntrack --ctstate NEW -j UDP
-A INPUT -p tcp --syn -m conntrack --ctstate NEW -j TCP
-A INPUT -p icmp -m conntrack --ctstate NEW -j ICMP

# Reject anything that's fallen through to this point
## Try to be protocol-specific w/ rejection message
-A INPUT -p udp -j REJECT --reject-with icmp-port-unreachable
-A INPUT -p tcp -j REJECT --reject-with tcp-reset
-A INPUT -j REJECT --reject-with icmp-proto-unreachable

# Commit the changes
COMMIT

*raw
:PREROUTING ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
COMMIT

*nat
:PREROUTING ACCEPT [0:0]
:INPUT ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
:POSTROUTING ACCEPT [0:0]
COMMIT

*security
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
COMMIT

*mangle
:PREROUTING ACCEPT [0:0]
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
:POSTROUTING ACCEPT [0:0]
COMMIT
"""
