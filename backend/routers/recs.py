from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.embedding_service import embed_item
from services.query_parser import parse_prompt
from services.mongo_client import get_items
from services.stub_store import search_products  # swap when index is ready

router = APIRouter()


class RecsQuery(BaseModel):
    user_id: str | None = None
    prompt: str | None = None


@router.post("/query")
def query_recs(body: RecsQuery):
    if not body.user_id and not body.prompt:
        raise HTTPException(status_code=400, detail="Provide user_id or prompt")

    if body.prompt:
        expanded = parse_prompt(body.prompt)
        vector = embed_item(expanded)
    else:
        items = get_items(body.user_id)
        if not items:
            raise HTTPException(status_code=404, detail="No items found for user")
        embeddings = [item["embedding"] for item in items if item.get("embedding")]
        if not embeddings:
            raise HTTPException(status_code=404, detail="No embeddings found for user items")
        n = len(embeddings[0])
        vector = [sum(e[i] for e in embeddings) / len(embeddings) for i in range(n)]

    results = search_products(vector, k=10)
    return {"results": results}
