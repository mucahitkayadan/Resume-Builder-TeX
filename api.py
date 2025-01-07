from fastapi import FastAPI
from src.api.main import create_app

app = create_app()

@app.get("/")
async def root():
    return {"message": "Welcome to ResumeBuilderTeX API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    ) 