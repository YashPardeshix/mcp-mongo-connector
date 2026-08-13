import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY") or os.getenv("OPENAI_API_KEY")
base_url = os.getenv("LLM_BASE_URL", "https://integrate.api.nvidia.com/v1")

client = OpenAI(api_key=api_key, base_url=base_url)


def translate_to_mongodb_query(
    user_request: str, schema_info: dict, model_name: str = "meta/llama-3.1-405b-instruct"
) -> dict:
    """Translates a natural language user request into a MongoDB query dictionary based on schema."""
    system_prompt = f"""
    You are an expert MongoDB Query Translator.
    Your job is to translate a user's natural language request into a valid MongoDB filter query object.
    
    Collection Schema Map:
    {json.dumps(schema_info, indent=2)}
    
    Rules:
    1. Output ONLY a valid JSON object representing the MongoDB query filter..
    2. Do NOT include markdown codeblocks (no ```json).
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