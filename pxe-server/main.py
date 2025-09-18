from fastapi import FastAPI, Depends, HTTPException, Request
from a2wsgi import ASGIMiddleware
from sqlalchemy import create_engine  # to thelo gia to create tou object
from sqlalchemy.engine import URL  # to thelo gia to url
from sqlalchemy.exc import OperationalError  # alios den fernei exception
from sqlalchemy.orm import sessionmaker, Session  # gia ta session
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy import insert, ForeignKey
from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.orm import declarative_base, relationship
from pydantic import BaseModel, validator  # to xriazome kai to validate pou ginete mesa sto class Firewallentry
from fastapi import Depends
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from datetime import datetime
from sqlalchemy import text, column
from jinja2 import Environment, FileSystemLoader
from typing import List
from typing import Optional
import subprocess
import os
from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from jinja2 import TemplateError
from fastapi.staticfiles import StaticFiles
from a2wsgi import ASGIMiddleware
from fastapi import Form
import hashlib
import bcrypt
from fastapi import Query




app = FastAPI()
application = ASGIMiddleware(app)
Base = declarative_base()
static_dir = os.path.join(os.path.dirname(__file__), "/api/static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

def generate_sha512_password(password: str):
    salt = os.urandom(16).hex()
    hashed_password = crypt.crypt(password, f"$6${salt}$")
    return hashed_password


class User(Base):
    __tablename__ = 'user_settings'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    hostname = Column(String(20))
    password = Column(String(200))
    username = Column(String(40))
    distro = Column(String(20))
    packets = relationship('Packet')

class Packet(Base):
    __tablename__ = 'user_packets'
    packet_id = Column(Integer, primary_key=True, autoincrement=True)
    packet_name = Column(String(50))
    user_id = Column(Integer, ForeignKey('user_settings.user_id'))

class UserCreate(BaseModel):
    hostname: str
    password: str
    username: str
    distro: str

class PacketCreate(BaseModel):
    packet_name: str
    user_id: int

class ListOfPacket(BaseModel):
    packets: List[PacketCreate]

def create_eng():
    url_object = URL.create(
        "postgresql+psycopg2",
        username="admin",
        password="666",
        host="10.0.48.100",
        database="users",
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

@app.get("/create-table/", response_model=None)
async def create_table():
    try:
        engine = create_eng()
        Base.metadata.create_all(engine)
        return "table created"
    except OperationalError as e:
        print("Connection error due to the following error: \n", str(e.orig))

@app.get("/add-user", response_class=HTMLResponse)
async def get_add_user_page():
    try:
        with open("/api/static/add_user.html") as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        print(f"Error loading add_user.html: {e}")
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>", status_code=400)

@app.post("/insert-user-page/", response_model=None)
async def insert_user_via_page(distro: str = Form(...) ,hostname: str = Form(...), password: str = Form(...), username: str = Form(...), packets: Optional[List[str]] = Form(None), db: Session = Depends(get_db)):
    try:
        print("xino1")
        print(password)
        #encrypted_password =generate_sha512_password(password)
        password_bytes = password.encode("utf-8")
        encrypted_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")
        print("xino2")
        new_user = User(
            hostname=hostname,
            password=encrypted_password,
            username=username,
            distro=distro
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        if packets:
            for packet_name in packets:
                already_inserted_packets = db.query(Packet).filter(Packet.packet_name == packet_name, Packet.user_id == new_user.user_id).first()  # checkarei diplopacketa
                #print(already_inserted_packets)
                if already_inserted_packets or packet_name == "":
                    continue
                new_packet = Packet(
                    packet_name=packet_name,
                    user_id=new_user.user_id
                )
                db.add(new_packet)
                db.commit()

        return {"message": "User  added successfully"}
    except OperationalError as e:
        db.rollback()
        print(f"Connection error due to the following error: \n{str(e.orig)}")
        raise HTTPException(status_code=500, detail=f"Connection error: {str(e.orig)}")


@app.get("/users/", response_model=List[UserCreate])
async def get_users(db: Session = Depends(get_db)):
    try:
        users = db.query(User).all()
        return [{"username": user.username, "hostname": user.hostname, "password": user.password, "distro": user.distro} for user in users]
    except OperationalError as e:
        print(f"Connection error due to the following error: \n{str(e.orig)}")
        raise HTTPException(status_code=500, detail=f"Connection error: {str(e.orig)}")




@app.get("/update-user", response_class=HTMLResponse)
async def get_add_user_page():
    try:
        with open("/api/static/update_user.html") as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        print(f"Error loading add_user.html: {e}")
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>", status_code=400)


@app.post("/update-user/")
async def update_rule(distro: str = Form(...),hostname: str = Form(...), password: str = Form(...), username: str = Form(...), db: Session = Depends(get_db)):

    fetched_user = db.query(User).filter(User.username == username).first()

    if not fetched_user:
        msg = "User not found."
        return HTMLResponse(content=f"<h1>Error: {msg}</h1>", status_code=400)

    try:
        if hostname:
            fetched_user.hostname = hostname
        if len(password) > 100:
            encrypted_password = password
            fetched_user.password = encrypted_password
        else:
            encrypted_password =generate_sha512_password(password)
            fetched_user.password = encrypted_password
        if username:
            fetched_user.username = username
        if distro:
            fetched_user.distro = distro
        db.commit()
        db.refresh(fetched_user)
        return {"message": "User updated successfully", "user_name": username}

    except OperationalError as e:
        print(f"Connection error due to the following error: \n{str(e.orig)}")
        raise HTTPException(status_code=500, detail=f"Connection error: {str(e.orig)}")


@app.post("/update-packets/")
async def update_rule(distro: str = Form(...),user_name: str = Form(...), hostname: str = Form(...), password: str = Form(...), packets: Optional[List[str]] = Form(None), db: Session = Depends(get_db)):
    fetched_user = db.query(User).filter(User.username == user_name).first()

    if hostname:
        fetched_user.hostname = hostname
    if len(password) > 100:
        encrypted_password = password
        fetched_user.password = encrypted_password
    else:
        password_bytes = password.encode("utf-8")
        encrypted_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")
        fetched_user.password = encrypted_password
    if distro:
        fetched_user.distro = distro

    db.add(fetched_user)
    db.commit()

    if packets:
        for packet_name in packets:
            already_inserted_packets = db.query(Packet).filter(Packet.packet_name == packet_name, Packet.user_id == fetched_user.user_id).first() #checkarei diplopacketa
            if already_inserted_packets or packet_name == "":
                continue

            new_packet = Packet(
                packet_name=packet_name,
                user_id=fetched_user.user_id
            )

            db.add(new_packet)
            db.commit()
            db.refresh(new_packet)

    return {"message": "User updated successfully", "user_name": user_name}


@app.get("/create", response_class=HTMLResponse)
async def get_create_configuration_page():
    try:
        with open("/api/static/configuration_create.html") as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        print(f"Error loading configuration_create.html: {e}")
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>", status_code=400)



@app.get("/create-configuration/")
async def create_configuration(username: str, lukpass: str, db: Session = Depends(get_db)):
    try:
        fetched_user = db.query(User).filter(User.username == username).first()

        if not fetched_user:
            return JSONResponse({"message": "User not found"}, status_code=404)

        print(fetched_user.user_id)
        print(fetched_user.password)
        print(fetched_user.hostname)
        print(fetched_user.distro)
         
        tftp_root_path = ""
        if fetched_user.distro == 'debian':
            tftp_root_path = '/srv/tftp-debian'
            env = Environment(loader=FileSystemLoader('/api/templates/'))
            try:
                template = env.get_template('tftp-base.j2')
            except TemplateError as e:
                print(f"Template error: {str(e)}")
                raise HTTPException(status_code=500, detail="Template error")
            try:
                content = template.render(tftp_root_path=tftp_root_path)
            except TemplateError as e:
                print(f"Error rendering template: {str(e)}")
                raise HTTPException(status_code=500, detail="Error rendering template")
            with open("/etc/dnsmasq.conf", 'w') as myfile:
                myfile.write(content)
        elif fetched_user.distro == 'ubuntu':
            tftp_root_path = '/srv/tftp'
            env = Environment(loader=FileSystemLoader('/api/templates/'))
            try:
                template = env.get_template('tftp-base.j2')
            except TemplateError as e:
                print(f"Template error: {str(e)}")
                raise HTTPException(status_code=500, detail="Template error")
            try:
                content = template.render(tftp_root_path=tftp_root_path)
            except TemplateError as e:
                print(f"Error rendering template: {str(e)}")
                raise HTTPException(status_code=500, detail="Error rendering template")
            with open("/etc/dnsmasq.conf", 'w') as myfile:
                myfile.write(content)

        command = '/etc/init.d/dnsmasq force-reload'
        #command = 'pkill -9 dnsmasq; /usr/sbin/dnsmasq --no-daemon --conf-file=/etc/dnsmasq.conf'
        restart = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(restart)

        fetched_packets = db.query(Packet).filter(Packet.user_id == fetched_user.user_id).all()  # Use .all() to get all packets
        packet_list = []
        for packt in fetched_packets:
            packet_list.append(packt.packet_name)

        packets_string = ""
        packets_string = " ".join(packet_list)

        if fetched_user.distro == 'ubuntu':
            env = Environment(loader=FileSystemLoader('/api/templates/'))
            try:
                template = env.get_template('basefile.j2')
            except TemplateError as e:
                print(f"Template error: {str(e)}")
                raise HTTPException(status_code=500, detail="Template error")

            try:
                content = template.render(hostname=fetched_user.hostname, password=fetched_user.password, username=fetched_user.username, packets=packet_list, lukpass=lukpass)
            except TemplateError as e:
                print(f"Error rendering template: {str(e)}")
                raise HTTPException(status_code=500, detail="Error rendering template")

            with open("/var/www/html/ubuntu/autoinstall-user-data.yml", 'w') as myfile:
                myfile.write(content)


        if fetched_user.distro == 'debian':
            env = Environment(loader=FileSystemLoader('/api/templates/'))
            try:
                template = env.get_template('debian-base.j2')
            except TemplateError as e:
                print(f"Template error: {str(e)}")
                raise HTTPException(status_code=500, detail="Template error")

            try:
                content = template.render(hostname=fetched_user.hostname, password=fetched_user.password, username=fetched_user.username, packets=packet_list, packets_string=packets_string)
            except TemplateError as e:
                print(f"Error rendering template: {str(e)}")
                raise HTTPException(status_code=500, detail="Error rendering template")

            with open("/var/www/html/ubuntu/debian/preseed.cfg", 'w') as myfile:
                myfile.write(content)


    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

    return {"message": "User updated successfully", "user_name": username}




@app.get("/delete", response_class=HTMLResponse)
async def get_delete_user_page():
    try:
        with open("/api/static/delete_user.html") as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        print(f"Error loading add_user.html: {e}")
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>", status_code=400)


@app.delete("/delete-user/{user_name}")
async def delete_user(user_name: str, db: Session = Depends(get_db)):
    fetched_user = db.query(User).filter(User.username == user_name).first()

    if not fetched_user:
        raise HTTPException(status_code=404, detail="User not found")

    fetch_packets = db.query(Packet).filter(Packet.user_id == fetched_user.user_id)

    for packet in fetch_packets:
        db.delete(packet)
    db.commit()

    db.delete(fetched_user)
    db.commit()
    return {"message": "User deleted successfully", "user_name": user_name}


@app.get("/user-packets/{user_name}")
async def get_user_packets(user_name: str, db: Session = Depends(get_db)):
    fetched_user = db.query(User).filter(User.username == user_name).first()

    if not fetched_user:
        raise HTTPException(status_code=404, detail="User not found")

    packets = db.query(Packet).filter(Packet.user_id == fetched_user.user_id).all()

    return [{"packet_name": packet.packet_name} for packet in packets]


@app.get("/delete-packet-per-user", response_class=HTMLResponse)
async def get_delete_user_page():
    try:
        with open("/api/static/delete_packet_per_user.html") as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        print(f"Error loading add_user.html: {e}")
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>", status_code=400)


@app.delete("/delete-user-packet/{user_name}/{packet_name}")
async def delete_user(user_name: str, packet_name: str, db: Session = Depends(get_db)):
    fetched_user = db.query(User).filter(User.username == user_name).first()
    if not fetched_user:
        raise HTTPException(status_code=404, detail="User not found")

    fetched_packet = db.query(Packet).filter(Packet.user_id == fetched_user.user_id, Packet.packet_name == packet_name).all()

    if not fetched_packet:
        raise HTTPException(status_code=404, detail="Packet not found")

    for pac in fetched_packet:
        db.delete(pac)

    db.commit()
    return {"message": "Packet delete", "Packet_name": packet_name}


@app.get("/pxe-portal", response_class=HTMLResponse)
async def get_home_page():
    with open("/api/static/index.html") as f:
        return HTMLResponse(content=f.read())
