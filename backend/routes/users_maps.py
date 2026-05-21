"""Routes /api/users/* et /api/maps/public/."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.responses import Response

from editor.map_manager import MapManager
from editor.user_manager import UserManager

router = APIRouter(tags=["users", "maps"])


@router.get("/users/")
def list_users():
    try:
        users = UserManager.list_users()
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/users/")
async def create_user(request: Request):
    try:
        body = await request.json()
        username = body.get("username")
        if not username:
            raise HTTPException(status_code=400, detail="Username is required")
        UserManager.create_user(username)
        return JSONResponse(
            content={"message": f"User {username} created"},
            status_code=201,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/users/{username}/maps/")
def list_user_maps(username: str):
    try:
        manager = MapManager(username)
        maps = manager.list_maps()
        return {"maps": maps}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/users/{username}/maps/")
async def create_map(username: str, request: Request):
    try:
        UserManager.ensure_user(username)
        manager = MapManager(username)
        map_data = await request.json()
        created_map = manager.create_map(map_data)
        return JSONResponse(content=created_map, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/users/{username}/maps/{map_id}/")
def get_map(username: str, map_id: str):
    try:
        manager = MapManager(username)
        map_data = manager.get_map(map_id)
        return map_data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Map not found") from None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/users/{username}/maps/{map_id}/")
async def update_map(username: str, map_id: str, request: Request):
    try:
        manager = MapManager(username)
        map_data = await request.json()
        updated_map = manager.update_map(map_id, map_data)
        return updated_map
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Map not found") from None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/users/{username}/maps/{map_id}/")
def delete_map(username: str, map_id: str):
    try:
        manager = MapManager(username)
        manager.delete_map(map_id)
        return Response(status_code=204)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/maps/public/")
def public_maps():
    try:
        maps = MapManager.list_all_public_maps()
        return {"maps": maps}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
