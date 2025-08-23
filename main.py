from fastapi import FastAPI, APIRouter
from fastapi.openapi.utils import get_openapi
import uvicorn, sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from src.app.routers import user_routes, post_routes, auth_routes

app = FastAPI(title="Cryptoweb Project", docs_url="/api/v1/docs", redoc_url="/api/v1/redoc", openapi_url="/api/v1/openapi.json")

app_v1 = APIRouter(prefix="/api/v1")

app_v1.include_router(user_routes.router_user)
app_v1.include_router(post_routes.router_post)
app_v1.include_router(auth_routes.router_auth)

app.include_router(app_v1)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version="0.0.0 alpha",
        routes=app.routes,
    )
    openapi_schema["servers"] = [{"url": "/api/v1"}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)