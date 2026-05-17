from fastapi import FastAPI
from app.routes import client, health

app = FastAPI(title="FastAPI App", version="1.0.0")

# Routers
app.include_router(health.router)
app.include_router(client.router)
