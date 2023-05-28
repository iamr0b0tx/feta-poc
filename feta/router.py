from fastapi import APIRouter, Depends, HTTPException

from feta.config import Config, ConfigNotFound, load_config
from feta.constants import CONFIG_PATH
from feta.principal import update_metadata, load_principal


def _get_config():
    try:
        return load_config(CONFIG_PATH)
    except ConfigNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


router = APIRouter()


def make_router(principal, principal_name, route_name):
    return APIRouter(
        prefix=f"/{principal}/{route_name}",
        tags=[f"{principal_name} / {route_name}"],
        responses={404: {"detail": "Not found"}}
    )


@router.get("/config")
async def get_config(config: Config = Depends(_get_config)):
    return config


@router.get("/metadata")
async def get_metadata(config: Config = Depends(_get_config)):
    principal = load_principal(config.principal_path)
    return principal.metadata


@router.post("/metadata")
async def post_metadata(metadata: dict, config: Config = Depends(_get_config)):
    principal = update_metadata(config.principal_path, metadata)
    return principal.metadata
