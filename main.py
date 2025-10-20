from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from Backend.connections.routes import router as api_router
from Backend.connections.mongo_db import init_mongo, close_mongo
from Backend.connections.redis_database import init_redis, close_redis
from Backend.connections.mysql_database import init_mysql, close_mysql

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_mongo() 
    await init_redis()
    init_mysql()
    print("✅ All connections initialized")
    
    yield
    
    close_mongo()  
    await close_redis()
    close_mysql()
    print("✅ All connections closed")

app = FastAPI(
    title="AutoMate AI API",
    description="Automation service backend",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/admin")
async def admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/health")
async def health():
    return {"status": "ok", "service": "AutoMate AI Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
# uvicorn main:app --reload --host 0.0.0.0
# ngrok http 8000
