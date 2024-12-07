from fastapi import FastAPI, HTTPException
import numpy as np
from pydantic import BaseModel
from middleware import log_requests
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router
from dashboard import router as dashboard_router
from product import router as product_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(dashboard_router, prefix="/dashboard")
app.include_router(product_router, prefix="/product")

# Apply Middleware
app.middleware("https")(log_requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to your needs
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check
@app.get("/")
async def root():
    return {"message": "AI REST API is running"}



