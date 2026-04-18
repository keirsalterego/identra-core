import os
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import router, memory_engine, llm_client
from src.memory.distiller import MemoryDistiller

log_dir = os.path.expanduser("~/.identra/logs")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO, 
    format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(log_dir, "brain.log"))
    ]
)
logger = logging.getLogger("brain")

distiller = MemoryDistiller(memory_engine, llm_client)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Identra Brain Service is starting up...")
    distiller_task = asyncio.create_task(distiller.start())
    yield
    logger.info("Identra Brain Service is shutting down...")
    await distiller.stop()
    distiller_task.cancel()

app = FastAPI(title="Identra Brain", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
