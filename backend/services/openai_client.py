from openai import OpenAI

client = OpenAI()


def combine_images(image_urls: list[str]):
    """Returns a base64 encoded result image."""

    input_images: list = [
        {
            "type": "input_image",
            "image_url": image_url,
            "detail": "auto",
        }
        for image_url in image_urls
    ]

    response = client.responses.create(
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
                        "text": "Combine these images.",
                    },
                    *input_images,
                ],
            }
        ],
    )

    image_result = next(
        output for output in response.output if output.type == "image_generation_call"
    )
    return image_result.result
