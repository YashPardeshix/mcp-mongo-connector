import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")
base_url = "https://integrate.api.nvidia.com/v1"

client = OpenAI(api_key=api_key, base_url=base_url)


def translate_to_mongodb_query(
    user_request: str,
    schema_info: dict,
    model_name: str = "nvidia/nemotron-3-ultra-550b-a55b",
) -> dict:
    """Translates a natural language user request into a MongoDB query dictionary.."""
    system_prompt = f"""
    You are a MongoDB Query Translator.
    Convert the user's natural language request into a valid MongoDB query filter JSON object based on the schema.
    
    Collection Schema Map:
    {json.dumps(schema_info, indent=2)}
    
    Rules:
    1. Output ONLY a valid JSON object representing the MongoDB query filter.
    2. Do NOT include markdown codeblocks or extra text.
    3. Use exact field names from the Schema Map.
    """

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_request},
        ],
        temperature=0.1,
    )

    raw_output = response.choices[0].message.content.strip()

    if raw_output.startswith("```"):
        raw_output = raw_output.split("```")[1]
        if raw_output.startswith("json"):
            raw_output = raw_output[4:]
        raw_output = raw_output.strip()

    return json.loads(raw_output)

if __name__ == "__main__":
    test_schema = {
        "collection": "products",
        "fields": {
            "title": "string",
            "price": "number",
            "category": "string",
            "in_stock": "boolean",
        },
    }

    test_request = (
        "Find all products in category shoes with price less than 100"
    )

    print("Sending request to NVIDIA model...")
    result = translate_to_mongodb_query(test_request, test_schema)
    print("\nTranslated Query Output:")
    print(json.dumps(result, indent=2))