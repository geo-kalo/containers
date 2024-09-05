from fastapi import FastAPI
from a2wsgi import ASGIMiddleware
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.exc import OperationalError #alios den fernei exception

app = FastAPI()
application = ASGIMiddleware(app)



def get_connection():
    url_object = URL.create(
        "postgresql+psycopg2",
        username="admin",
        password="666",
        host="192.168.199.8",
        database="firewall",
    )
    print(url_object)
    return create_engine(url_object)


@app.get("/test")
async def read_test():
    try:
        engine = get_connection()
        connection = engine.connect()
        return "Connected to database"
    except OperationalError as e:
        print("Connection error due to the following error: \n", e)
        return("Connection error due to the following error: \n", e)


    #finally:




