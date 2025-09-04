from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import ping
from .config.settings import settings

# Create FastAPI app instance
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ping.router, prefix="/api/v1", tags=["ping"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to MYUBER API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "MYUBER API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

