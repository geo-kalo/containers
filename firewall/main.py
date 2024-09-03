from fastapi import FastAPI
from a2wsgi import ASGIMiddleware

app = FastAPI()
application = ASGIMiddleware(app)

@app.get("/test")
async def read_test():
    return {"message": "Hello, this is the /test endpoint!"}


