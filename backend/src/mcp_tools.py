from mcp.server.mcpserver import MCPServer

from mongodb import client
from translator import (
    translate_to_mongodb_document,
    translate_to_mongodb_query,
)


mcp = MCPServer("Universal MongoDB Connector")


@mcp.tool(
    name="query-collection",
    description="Query a MongoDB collection using a natural-language request.",
)
def query_collection(
    collection_name: str,
    query: str,
) -> list[dict]:
    """Find documents in a MongoDB collection using natural language."""

    database = client["mcp_mongo_connector"]
    collection = database[collection_name]

    schema_info = {
        "collection": collection_name,
        "fields": {
            "title": "string",
            "price": "number",
            "category": "string",
            "brand": "string",
            "color": "string",
            "in_stock": "boolean",
        },
    }

    mongo_filter = translate_to_mongodb_query(
        user_request=query,
        schema_info=schema_info,
    )

    return list(
        collection.find(
            mongo_filter,
            {"_id": 0},
        )
    )


@mcp.tool(
    name="insert-document",
    description="Insert a document into a MongoDB collection using natural language.",
)
def insert_document(
    collection_name: str,
    document_description: str,
) -> dict:
    """Create and insert a document described in natural language."""

    database = client["mcp_mongo_connector"]
    collection = database[collection_name]

    schema_info = {
        "collection": collection_name,
        "fields": {
            "title": "string",
            "price": "number",
            "category": "string",
            "brand": "string",
            "color": "string",
            "in_stock": "boolean",
        },
    }

    document = translate_to_mongodb_document(
        document_description=document_description,
        schema_info=schema_info,
    )

    result = collection.insert_one(document)

    inserted_document = collection.find_one(
        {"_id": result.inserted_id},
        {"_id": 0},
    )

    return {
        "inserted_id": str(result.inserted_id),
        "document": inserted_document,
    }


@mcp.tool(
    name="update-document",
    description="Update documents in a MongoDB collection.",
)
def update_document(
    collection_name: str,
    filter_description: str,
    update_description: str,
) -> dict:
    """Update matching documents. Translation will be added next."""

    raise NotImplementedError(
        "Update translation is the next implementation step."
    )


@mcp.tool(
    name="delete-document",
    description="Delete documents from a MongoDB collection.",
)
def delete_document(
    collection_name: str,
    condition_description: str,
) -> dict:
    """Delete matching documents. Translation will be added next."""

    raise NotImplementedError(
        "Delete translation is the next implementation step."
    )


@mcp.tool(
    name="describe-schema",
    description="Describe the structure of a MongoDB collection.",
)
def describe_schema(
    collection_name: str,
) -> dict:
    """Return a basic description of the fields in a collection."""

    database = client["mcp_mongo_connector"]
    collection = database[collection_name]

    sample_document = collection.find_one()

    if sample_document is None:
        return {
            "collection": collection_name,
            "fields": {},
            "message": "Collection is empty.",
        }

    fields = {}

    for field_name, value in sample_document.items():
        if field_name == "_id":
            continue

        if isinstance(value, bool):
            field_type = "boolean"
        elif isinstance(value, (int, float)):
            field_type = "number"
        elif isinstance(value, str):
            field_type = "string"
        elif isinstance(value, list):
            field_type = "array"
        elif isinstance(value, dict):
            field_type = "object"
        else:
            field_type = type(value).__name__

        fields[field_name] = field_type

    return {
        "collection": collection_name,
        "fields": fields,
    }
