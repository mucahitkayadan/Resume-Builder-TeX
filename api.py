import uvicorn
from src.api.main import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="debug"
    ) 