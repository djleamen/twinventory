import base64
import os
from pydantic import BaseModel
from openai import OpenAI


class ItemTags(BaseModel):
    category: str  
    color: str     
    style: str     
    size: str      


_client = OpenAI()  # reads OPENAI_API_KEY from env; load_dotenv() must be called before import

_PROMPT = """You are a fashion tagging assistant. Analyze this clothing item image and return structured tags.

- category: the type of clothing (shirt, t-shirt, dress, pants, jeans, jacket, coat, skirt, shorts, shoes, sneakers, boots, bag, accessory, or other)
- color: the primary color in plain English (e.g. white, black, navy, red, olive)
- style: the overall style (casual, formal, sporty, streetwear, vintage, bohemian, minimalist, or other)
- size: if a size label is visible return it (XS, S, M, L, XL, XXL), otherwise return "unknown"
"""


def _mime(image_bytes: bytes) -> str:
    return "image/png" if image_bytes[:4] == b"\x89PNG" else "image/jpeg"


def tag_item(image_bytes: bytes) -> ItemTags:
    b64 = base64.b64encode(image_bytes).decode()
    response = _client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{_mime(image_bytes)};base64,{b64}"}},
                    {"type": "text", "text": _PROMPT},
                ],
            }
        ],
        response_format=ItemTags,
    )
    return response.choices[0].message.parsed
