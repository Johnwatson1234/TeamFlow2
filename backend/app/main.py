from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.seed import seed_database
from app.db.session import Base, engine


Base.metadata.create_all(bind=engine)
seed_database()

app = FastAPI(title="TeamFlow API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
def read_root():
    return {"name": "TeamFlow API", "status": "ok"}
