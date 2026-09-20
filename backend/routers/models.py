from fastapi import APIRouter
from pydantic import BaseModel

from services.meshy_client import get_3d_model

router = APIRouter(prefix="/models", tags=["models"])


class ConvertRequest(BaseModel):
    image_url: str


@router.post("/convert")
def convert_route(request: ConvertRequest):
    model_url = get_3d_model(request.image_url)
    return {"model_url": model_url}
