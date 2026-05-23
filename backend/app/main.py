import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import conversations, chat, ingest, metrics


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.workers.log_consumer import run_consumer
    task = asyncio.create_task(run_consumer())
    yield
    task.cancel()


app = FastAPI(title="Ollive AI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(conversations.router)
app.include_router(chat.router)
app.include_router(ingest.router)
app.include_router(metrics.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
