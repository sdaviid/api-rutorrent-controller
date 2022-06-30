from fastapi import APIRouter
from app.api.routes import route_torrent
from app.api.routes import route_server


api_router = APIRouter()
api_router.include_router(route_torrent.router, prefix="/torrent", tags=["torrent"])
api_router.include_router(route_server.router, prefix="/server", tags=["server"])