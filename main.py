from fastapi import FastAPI
import uvicorn, sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))
from src.app.routers import posts

app = FastAPI()
app.include_router(posts.router_users)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)