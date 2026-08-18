import json
from db import execute_query
from mcp.server.fastmcp import FastMCP
from translator import translate_to_mongodb_query

mcp = FastMCP("MongoDB Universal Connector")

COLLECTION_SCHEMAS = {
    "products": {
        "title": "string",
        "price": "number",
        "category": "string",
        "in_stock": "boolean",
    },
    "users": {
        "name": "string",
        "email": "string",
        "role": "string",
        "age": "number",
    },
    "orders": {
        "order_id": "string",
        "user_email": "string",
        "total_amount": "number",
        "status": "string",
    },
}


@mcp.tool()
def query_collection(collection_name: str, query: str) -> str:
    """Executes a natural language query against any MongoDB collection and returns matching documents."""
    schema = COLLECTION_SCHEMAS.get(collection_name, {})
    query_filter = translate_to_mongodb_query(
        user_request=query, schema_info=schema
    )

    documents = execute_query(collection_name, query_filter)
    response_payload = {
        "collection": collection_name,
        "translated_query": query_filter,
        "results": documents,
    }

    return json.dumps(response_payload, indent=2)


if __name__ == "__main__":
    print("Testing query_collection MCP tool in isolation...")

    test_result = query_collection(
        collection_name="products",
        query="Find shoes under 100 dollars",
    )

    print("\nMCP Tool Response Payload:")
    print(test_result)