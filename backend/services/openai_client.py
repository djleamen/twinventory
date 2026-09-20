from functools import lru_cache

from openai import OpenAI


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    return OpenAI()


TRY_ON_PROMPT = (
    "The first image is a person. Dress that exact person in the clothing items "
    "shown in the other images. Keep the person's face, hair, pose, and body "
    "identical to the first image. Use a plain, pure white background."
)


def combine_images(image_urls: list[str]) -> str | None:
    """Returns a base64 encoded result image, or None if the model refused."""

    input_images: list = [
        {
            "type": "input_image",
            "image_url": image_url,
            "detail": "auto",
        }
        for image_url in image_urls
    ]

    response = get_openai_client().responses.create(
        model="gpt-5.6-luna",
        tools=[
            {
                "type": "image_generation",
                "quality": "auto",
            }
        ],
        tool_choice={"type": "image_generation"},
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": TRY_ON_PROMPT,
                    },
                    *input_images,
                ],
            }
        ],
    )

    image_result = next(
        (output for output in response.output if output.type == "image_generation_call"),
        None,
    )
    return image_result.result if image_result else None
