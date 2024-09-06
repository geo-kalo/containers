from fastapi import FastAPI
from a2wsgi import ASGIMiddleware
from sqlalchemy import create_engine # to thelo gia to create tou object
from sqlalchemy.engine import URL # to thelo gia to url
from sqlalchemy.exc import OperationalError #alios den fernei exception
from sqlalchemy.orm import sessionmaker, Session # gia ta session
from sqlalchemy.ext.declarative import declarative_base #create tables
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy import insert
from pydantic import BaseModel
from fastapi import Depends


from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from datetime import datetime

app = FastAPI()
application = ASGIMiddleware(app)

#https://jnikenoueba.medium.com/using-fastapi-with-sqlalchemy-5cd370473fe5
#https://medium.com/technology-hits/database-queries-in-python-sqlalchemy-postgresql-e90afe0a06b4
#https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_core_connecting_to_database.htm
#https://www.datacamp.com/tutorial/sqlalchemy-tutorial-examples
#https://jnikenoueba.medium.com/using-fastapi-with-sqlalchemy-5cd370473fe5

Base = declarative_base()

class Firewall(Base):
    __tablename__ = 'firewall'
    rule_id = Column(Integer, primary_key=True, autoincrement=True)
    chain = Column(String(15), nullable=False)  # e.g., INPUT, OUTPUT, FORWARD
    protocol = Column(String(10))  # e.g., tcp, udp, icmp
    src_ip = Column(String(15))  # Source IP address
    dst_ip = Column(String(15))  # Destination IP address
    src_port = Column(Integer)  # Source Port
    dst_port = Column(Integer)  # Destination Port
    action = Column(String(10), nullable=False)  # e.g., ACCEPT, DROP, REJECT
    in_interface = Column(String(20))  # Incoming network interface
    out_interface = Column(String(20))  # Outgoing network interface
    state = Column(String(20))  # Connection state (e.g., NEW, ESTABLISHED)
    comment = Column(Text)  # Optional comment about the rule
    #log = Column(Boolean, default=False)  # Whether to log the rule
    created_at = Column(DateTime, default=datetime.utcnow)  # Creation timestamp
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last update timestamp


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

#database open / sessions
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


@app.post("/create-table/{item}",  response_model=None)
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
async  def insert_rule(rule: Firewallentry, db: Session = Depends(get_db)):
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
            comment=rule.comment
        )
        db.add(new_rule)
        db.commit()
        db.refresh(new_rule)
        return {"message": "Firewall rule added successfully"}
    except OperationalError as e:
        db.rollback()
        print(f"Connection error due to the following error: \n{str(e.orig)}")
        raise HTTPException(status_code=500, detail=f"Connection error: {str(e.orig)}")






#@app.get("/test")
#async def read_test():
#    try:
#        connection = get_connection()
#        return "Connected to database"
#    except OperationalError as e:
#        print("Connection error due to the following error: \n", str(e.orig))
#        return(str(e.orig))
#    finally:
#        connection.close()

    #finally:




#curl -k -X 'POST' https://localhost:49888/insert-rule/   -H 'Content-Type: application/json'   -d '{
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
