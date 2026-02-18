from fastapi import APIRouter

from src.interface.api.v1 import v1_router

app_router = APIRouter(prefix='/api')
router_list = [v1_router]

for router in router_list:
    app_router.include_router(router)
