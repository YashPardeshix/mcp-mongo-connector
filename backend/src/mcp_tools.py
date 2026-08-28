from mcp.server.mcpserver import MCPServer

from mongodb import client
from translator import translate_to_mongodb_query


mcp = MCPServer("Universal MongoDB Connector")


@mcp.tool(
    name="query-collection",
    description="Query a MongoDB collection using a natural-language request.",
)
def query_collection(
    collection_name: str,
    query: str,
) -> list[dict]:
    """
    Find documents in a MongoDB collection using natural language.
    """

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

    results = list(
        collection.find(
            mongo_filter,
            {"_id": 0},
        )
    )

    return results