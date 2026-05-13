from fastapi import FastAPI
from src.fast_api.routes.ask import router

app = FastAPI()

app.include_router(router)