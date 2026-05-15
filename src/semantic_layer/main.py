from fastapi import FastAPI
from routes.ask import router as ask_router
from routes.build_dbt import router as build_dbt_router
from routes.indexing import router as indexing_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ask_router)
app.include_router(build_dbt_router)
app.include_router(indexing_router)