from fastapi import FastAPI
import uvicorn, sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))
from src.app.routers import user_routes, post_routes

app = FastAPI()
app.include_router(user_routes.router_user)
app.include_router(post_routes.router_post)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)