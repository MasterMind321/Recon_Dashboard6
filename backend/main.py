from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from .routes.tool_routes import router as tool_router
from .routes.scan_routes import router as scan_router
from .routes.target_routes import router as target_router
from .services.database import close_database
import logging

# Create the main app without a prefix
app = FastAPI(title="ReconFlow API", version="2.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Health check endpoint
@api_router.get("/")
async def root():
    return {"message": "ReconFlow API v2.0 is running"}

# Include routers
api_router.include_router(tool_router)
api_router.include_router(scan_router)
api_router.include_router(target_router)

# Include the router in the main app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_database()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)