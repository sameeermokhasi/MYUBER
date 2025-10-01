from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# These imports bring in your database connection, models, and routes
from .database import engine
from . import models
from .routes import ping, rides
from .config.settings import settings

# This crucial line tells SQLAlchemy to create the database tables
# based on the models defined in models.py.
models.Base.metadata.create_all(bind=engine)

# --- Create FastAPI app instance ---
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="1.0.0"
)

# --- Add CORS middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
app.include_router(ping.router, prefix="/api/v1", tags=["ping"])
app.include_router(rides.router, prefix="/api", tags=["Rides"])

# --- General API Endpoints ---
@app.get("/")
async def root():
    return {"message": "Welcome to MYUBER API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "MYUBER API"}

# --- Main execution block ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )