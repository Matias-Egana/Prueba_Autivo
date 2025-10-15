from fastapi import FastAPI
from .routes import router

app = FastAPI(title="Autivo API")
app.include_router(router)