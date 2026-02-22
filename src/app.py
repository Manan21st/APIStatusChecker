from fastapi import FastAPI

from api import health, status
from api.monitor import lifespan

app = FastAPI(title="API Status Checker", lifespan=lifespan)

app.include_router(health.router, prefix="/api")
app.include_router(status.router, prefix="/api")