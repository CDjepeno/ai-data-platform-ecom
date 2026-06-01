from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from routes.ask import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)

app.include_router(router)
