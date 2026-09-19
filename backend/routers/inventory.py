import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from services.rembg_service import remove_background
from services.tagging_service import tag_item
from services.embedding_service import embed_item
from services.mongo_client import save_item, get_items

router = APIRouter()

UPLOADS_DIR = Path(__file__).parent.parent / "uploads"


@router.post("/upload")
def upload_item(user_id: str, file: UploadFile = File(...)):
    image_bytes = file.file.read()

    cutout_bytes = remove_background(image_bytes)

    tags = tag_item(image_bytes)

    description = f"{tags.category}, {tags.color}, {tags.style}"
    embedding = embed_item(description)

    filename = f"{uuid.uuid4()}.png"
    (UPLOADS_DIR / filename).write_bytes(cutout_bytes)
    image_url = f"/static/{filename}"

    item_id = save_item({
        "user_id": user_id,
        "image_url": image_url,
        "category": tags.category,
        "color": tags.color,
        "style": tags.style,
        "size": tags.size,
        "embedding": embedding,
    })

    return {"item_id": item_id, "tags": tags, "image_url": image_url}


@router.get("/{user_id}")
def get_inventory(user_id: str):
    return {"user_id": user_id, "items": get_items(user_id)}
