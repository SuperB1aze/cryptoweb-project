from fastapi import FastAPI
import uvicorn
from src.app.routers import posts

app = FastAPI()
app.include_router(posts.router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)