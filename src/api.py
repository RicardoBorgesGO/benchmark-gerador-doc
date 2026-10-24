from pydantic import BaseModel, HttpUrl
from pipeline import generate
from fastapi import FastAPI
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

app = FastAPI(title="API de Geração de Documentos")

class RepoRequest(BaseModel):
    github_url: HttpUrl

@app.post("/generate")
async def main(payload: RepoRequest):
    logging.info("REQUEST RECEIVED")
    repository_url = str(payload.github_url)
    generate(repository_url)
    return 200