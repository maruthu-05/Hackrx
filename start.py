"""
Production startup script for the LLM Query-Retrieval System
Handles both development and production environments
"""

import os
import uvicorn
from main import app

def main():
    """Start the application with appropriate configuration"""
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    workers = int(os.getenv("WORKERS", 1))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    # Production vs Development settings
    if os.getenv("ENVIRONMENT") == "production":
        # Production configuration
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            workers=workers,
            reload=False,
            access_log=True,
            log_level="info"
        )
    else:
        # Development configuration
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="debug"
        )

if __name__ == "__main__":
    main()