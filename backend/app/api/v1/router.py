from fastapi import APIRouter

from app.api.v1 import containers, notes, search

api_router = APIRouter()

api_router.include_router(notes.router, prefix="/notes", tags=["notes"])
api_router.include_router(containers.router, prefix="/containers", tags=["containers"])
api_router.include_router(search.router, tags=["search"])
