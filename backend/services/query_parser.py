from openai import OpenAI

_client = OpenAI()

_PROMPT = """You are a fashion search assistant. Expand a user's short style prompt into a rich search query for a clothing recommendation engine.

Return only a comma-separated list of relevant fashion terms — clothing types, styles, occasions, colors, and aesthetics. No explanation, no punctuation other than commas.

Examples:
- "wedding" → "formal wear, dress, suit, elegant, wedding guest, pastel, floral, midi dress, blazer"
- "beach day" → "swimwear, linen, shorts, sundress, casual, light colors, sandals, cover-up"
- "job interview" → "business casual, blazer, trousers, button-down, smart, neutral colors, professional"
"""


def parse_prompt(text: str) -> str:
    response = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()
