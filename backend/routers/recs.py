from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class RecsQuery(BaseModel):
    user_id: str | None = None
    prompt: str | None = None


@router.post("/query")
def query_recs(body: RecsQuery):
    # style vector (user_id path) 
    raise NotImplementedError
