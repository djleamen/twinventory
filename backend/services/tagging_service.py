from pydantic import BaseModel


class ItemTags(BaseModel):
    category: str
    color: str
    style: str
    size: str


def tag_item(image_bytes: bytes) -> ItemTags:
    # TODO Step 2: OpenAI vision call with structured output → ItemTags
    raise NotImplementedError
