from openai import OpenAI

_client = OpenAI()  

_MODEL = "text-embedding-3-small"  # 1536-dim, reuse this model for product embeddings too


def embed_item(description: str) -> list[float]:
    response = _client.embeddings.create(model=_MODEL, input=description)
    return response.data[0].embedding
