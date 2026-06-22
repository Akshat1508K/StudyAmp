"""
Simple script to start the backend server.
Run: python start_backend.py
"""
import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("Starting StudyAmp AI Backend Server")
    print("=" * 60)
    print("\nBackend will be available at: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("\nPress CTRL+C to stop the server")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
