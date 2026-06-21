"""
Start backend WITHOUT reload to ensure clean start
"""
import uvicorn
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    print("="*60)
    print("Starting Backend (NO RELOAD MODE)")
    print("="*60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload to avoid cache issues
        log_level="info"
    )
