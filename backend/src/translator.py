import json
import os
from typing import Any
from dotenv import load_dotenv
from openai import OpenAI
from mongo_query_schema import MongoQueryFilter, MongoDocument


load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "nvidia/nemotron-3-ultra-550b-a55b"

if not NVIDIA_API_KEY:
    raise RuntimeError(
        "NVIDIA_API_KEY is not set in your .env file or environment."
    )

client = OpenAI(
    api_key=NVIDIA_API_KEY,
    base_url=NVIDIA_BASE_URL,
)


def _validate_schema_info(schema_info: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(schema_info, dict) or not schema_info:
        raise ValueError("schema_info must be a non-empty dictionary.")

    fields = schema_info.get("fields")

    if not isinstance(fields, dict) or not fields:
        raise ValueError(
            "schema_info must contain a non-empty 'fields' dictionary."
        )

    return fields


def translate_to_mongodb_query(
    user_request: str,
    schema_info: dict[str, Any],
    model_name: str = DEFAULT_MODEL,
) -> dict[str, Any]:
    """Translate a natural-language request into a MongoDB filter."""

    if not user_request.strip():
        raise ValueError("user_request cannot be empty.")

    fields = _validate_schema_info(schema_info)
    allowed_fields = set(fields.keys())

    system_prompt = f"""
You are a MongoDB query translator.

Convert the user's natural-language request into ONE valid MongoDB
filter JSON object using ONLY the supplied collection schema.

Collection schema:
{json.dumps(schema_info, indent=2)}

Rules:
1. Return ONLY a valid JSON object.
2. Use ONLY field names that exist in the supplied schema.
3. Preserve EVERY explicit condition from the user's request when
   the schema contains a matching field.
4. Do not invent fields, values, or conditions.
5. Use valid MongoDB filter syntax.
6. For comparisons use $lt, $lte, $gt, $gte, or $ne.
7. Use the correct value type from the schema.
8. Do not return Markdown, explanations, or extra text.
"""

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_request},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("The NVIDIA model returned no content.")

    try:
        translated_query = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Translator returned invalid JSON: {content}"
        ) from exc

    if not isinstance(translated_query, dict):
        raise ValueError("Translator output must be a JSON object.")


    validated = MongoQueryFilter(**translated_query)
    dumped = validated.model_dump(by_alias=True)

    def _strip_none(value):
        if isinstance(value, dict):
            return {k: _strip_none(v) for k, v in value.items() if v is not None}
        return value

    cleaned = {key: _strip_none(value) for key, value in dumped.items() if value is not None}
    cleaned = {key: value for key, value in cleaned.items() if value != {}}

    return cleaned


def translate_to_mongodb_document(
    document_description: str,
    schema_info: dict[str, Any],
    model_name: str = DEFAULT_MODEL,
) -> dict[str, Any]:
    """Translate a natural-language document description into a MongoDB document."""

    if not document_description.strip():
        raise ValueError("document_description cannot be empty.")

    fields = _validate_schema_info(schema_info)
    allowed_fields = set(fields.keys())

    system_prompt = f"""
You are a MongoDB document translator.

Convert the user's natural-language document description into ONE
valid JSON document that can be inserted into the supplied collection.

Collection schema:
{json.dumps(schema_info, indent=2)}

Rules:
1. Return ONLY a valid JSON object.
2. Use ONLY fields that exist in the supplied schema.
3. Extract every piece of information explicitly provided by the user
   when a matching schema field exists.
4. Do not invent fields.
5. Do not invent values that the user did not provide.
6. Use the correct data type for each field according to the schema.
7. Do not create or include MongoDB _id values.
8. Do not return Markdown, explanations, or extra text.
"""

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": document_description},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("The NVIDIA model returned no content.")

    try:
        translated_document = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Document translator returned invalid JSON: {content}"
        ) from exc

    if not isinstance(translated_document, dict):
        raise ValueError("Document translator output must be a JSON object.")

    validated = MongoDocument(**translated_document)
    dumped = validated.model_dump(by_alias=True)
    cleaned = {key: value for key, value in dumped.items() if value is not None}
    return cleaned




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

    test_description = (
        "Add a red Nike shoe costing ₹4,999 that is in stock."
    )

    print("Sending insert request to NVIDIA model...")

    result = translate_to_mongodb_document(
        document_description=test_description,
        schema_info=test_schema,
    )

    print("\nTranslated MongoDB Document:")
    print(json.dumps(result, indent=2))
