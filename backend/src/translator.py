import json
import os
from typing import Any
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "nvidia/nemotron-3-ultra-550b-a55b"

if not NVIDIA_API_KEY:
    raise RuntimeError(
        "NVIDIA_API_KEY is not set. Add it to your environment or .env file."
    )

client = OpenAI(
    api_key=NVIDIA_API_KEY,
    base_url=NVIDIA_BASE_URL,
)


def translate_to_mongodb_query(
    user_request: str,
    schema_info: dict[str, Any],
    model_name: str = DEFAULT_MODEL,
) -> dict[str, Any]:
    """
    Translate a natural-language MongoDB query request into a
    structured MongoDB filter object.

    This function only handles translation.
    It does not validate the translated query against our internal
    Pydantic model and it does not execute anything against MongoDB.
    """

    if not user_request.strip():
        raise ValueError("user_request cannot be empty.")

    if not isinstance(schema_info, dict) or not schema_info:
        raise ValueError("schema_info must be a non-empty dictionary.")

    system_prompt = f"""
You are a MongoDB query translator.

Convert the user's natural-language request into a valid MongoDB
query filter JSON object based only on the provided collection schema.

Collection schema:
{json.dumps(schema_info, indent=2)}

Rules:
1. Return ONLY a valid JSON object.
2. Do not return Markdown, code fences, explanations, or extra text.
3. Use only field names that exist in the provided schema.
4. Use valid MongoDB filter syntax.
5. Do not invent fields that are not present in the schema.
6. Preserve every explicit condition expressed in the user's request.
   If the schema contains a field that corresponds to a condition,
   include that condition in the output.
7. Do not omit a relevant condition simply because another condition
   already identifies the same type of product.
"""

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_request,
            },
        ],
        temperature=0.1,
    )

    message = response.choices[0].message.content

    if not message:
        raise RuntimeError("The translation model returned an empty response.")

    raw_output = message.strip()

    if raw_output.startswith("```"):
        parts = raw_output.split("```")

        if len(parts) >= 3:
            raw_output = parts[1].strip()

            if raw_output.lower().startswith("json"):
                raw_output = raw_output[4:].strip()

    try:
        translated_query = json.loads(raw_output)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Translator returned invalid JSON: {raw_output}"
        ) from exc

    if not isinstance(translated_query, dict):
        raise ValueError(
            "Translator output must be a JSON object."
        )

    return translated_query


if __name__ == "__main__":
    test_schema = {
        "collection": "products",
        "fields": {
            "title": "string",
            "price": "number",
            "category": "string",
            "brand": "string",
            "color": "string",
            "in_stock": "boolean",
        },
    }

    test_request = "Find blue Nike shoes under ₹3,000 that are currently in stock."

    print("Sending request to NVIDIA model...")

    result = translate_to_mongodb_query(
        user_request=test_request,
        schema_info=test_schema,
    )

    print("\nTranslated Query Output:")
    print(json.dumps(result, indent=2))