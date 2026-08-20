import json
from db import execute_query
from mcp.server.mcpserver import MCPServer
from translator import translate_to_mongodb_query

mcp = MCPServer("MongoDB Universal Connector")

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


@mcp.tool()
def describe_schema(collection_name: str) -> str:
    """Returns the schema and field types for a specific MongoDB collection."""
    schema = COLLECTION_SCHEMAS.get(collection_name, {})
    return json.dumps({"collection": collection_name, "schema": schema}, indent=2)


def insert_doc(collection_name: str, document: dict) -> str:
    """Inserts a single document into MongoDB and returns the inserted ID as a string."""
    collection = db[collection_name]
    result = collection.insert_one(document)
    return str(result.inserted_id)




if __name__ == "__main__":
    print("Testing query_collection MCP tool in isolation...")

    test_result = query_collection(
        collection_name="products",
        query="Find shoes under 100 dollars",
    )

    print("\nMCP Tool Response Payload:")
    print(test_result)