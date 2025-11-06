from fastapi import FastAPI
from mangum import Mangum

app = FastAPI(title="Aplicacion Senas - Lambda Example")


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.get("/v1/hello")
def hello():
    return {"message": "Hello from Lambda FastAPI scaffold"}


# Mangum handler for AWS Lambda
handler = Mangum(app)
