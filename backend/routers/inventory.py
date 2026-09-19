from fastapi import APIRouter, UploadFile, File

router = APIRouter()


@router.post("/upload")
def upload_item(user_id: str, file: UploadFile = File(...)):
    # rembg → tag → embed → save_item
    raise NotImplementedError


@router.get("/{user_id}")
def get_inventory(user_id: str):
    # return get_items(user_id)
    raise NotImplementedError
