from fastapi import APIRouter
from pydantic import BaseModel

from services.meshy_client import get_3d_model
from services.mongo_client import try_on_result_exists

router = APIRouter(prefix="/models", tags=["models"])


class ConvertRequest(BaseModel):
    image_url: str
    # Try-on cache key from POST /products/try; lets the same outfit reuse its 3D model.
    cache_key: str | None = None


@router.post("/convert")
def convert_route(request: ConvertRequest):
    # Only honor keys for try-ons we actually stored (never ephemeral content).
    cache_key = (
        request.cache_key
        if request.cache_key and try_on_result_exists(request.cache_key)
        else None
    )
    model_url = get_3d_model(request.image_url, cache_key=cache_key)
    return {"model_url": model_url}
