from mongodb import client
from translator import translate_to_mongodb_document, translate_to_mongodb_query
from mcp_tool_schema import (
    QueryCollectionInput,
    InsertDocumentInput,
    UpdateDocumentInput,
    DeleteDocumentInput,
    DescribeSchemaInput,
)

mcp = MCPServer("Universal MongoDB Connector")

COLLECTION_SCHEMAS = {
    "products": {"title": "string", "price": "number", "category": "string",
                 "brand": "string", "color": "string", "in_stock": "boolean"},
    "users": {"name": "string", "email": "string", "role": "string", "age": "number"},
    "orders": {"order_id": "string", "user_email": "string",
               "total_amount": "number", "status": "string"},
}


@mcp.tool(name="describe-schema", description="Returns the schema and field types for a MongoDB collection.")
def describe_schema(collection_name: str) -> dict:
    validated_input = DescribeSchemaInput(collection_name=collection_name)
    return {"collection": validated_input.collection_name,
            "fields": COLLECTION_SCHEMAS.get(validated_input.collection_name, {})}


@mcp.tool(name="query-collection", description="Query a MongoDB collection using natural language.")
def query_collection(collection_name: str, query: str) -> list[dict]:
    validated_input = QueryCollectionInput(collection_name=collection_name, query=query)
    database = client["mcp_mongo_connector"]
    collection = database[validated_input.collection_name]
    schema_info = {"collection": validated_input.collection_name,
                   "fields": COLLECTION_SCHEMAS.get(validated_input.collection_name, {})}
    mongo_filter = translate_to_mongodb_query(user_request=validated_input.query, schema_info=schema_info)
    return list(collection.find(mongo_filter, {"_id": 0}))


@mcp.tool(name="insert-document", description="Insert a document using natural language.")
def insert_document(collection_name: str, document_description: str) -> dict:
    validated_input = InsertDocumentInput(collection_name=collection_name, document_description=document_description)
    database = client["mcp_mongo_connector"]
    collection = database[validated_input.collection_name]
    schema_info = {"collection": validated_input.collection_name,
                   "fields": COLLECTION_SCHEMAS.get(validated_input.collection_name, {})}
    document = translate_to_mongodb_document(document_description=validated_input.document_description, schema_info=schema_info)
    result = collection.insert_one(document)
    return {"inserted_id": str(result.inserted_id),
            "document": collection.find_one({"_id": result.inserted_id}, {"_id": 0})}


@mcp.tool(name="update-document", description="Update documents matching a natural-language condition.")
def update_document(collection_name: str, filter_description: str, update_description: str) -> dict:
    validated_input = UpdateDocumentInput(collection_name=collection_name,
                                           filter_description=filter_description,
                                           update_description=update_description)
    database = client["mcp_mongo_connector"]
    collection = database[validated_input.collection_name]
    schema_info = {"collection": validated_input.collection_name,
                   "fields": COLLECTION_SCHEMAS.get(validated_input.collection_name, {})}
    mongo_filter = translate_to_mongodb_query(user_request=validated_input.filter_description, schema_info=schema_info)
    update_fields = translate_to_mongodb_document(document_description=validated_input.update_description, schema_info=schema_info)
    result = collection.update_many(mongo_filter, {"$set": update_fields})
    return {"matched": result.matched_count, "modified": result.modified_count}


@mcp.tool(name="delete-document", description="Delete documents matching a natural-language condition.")
def delete_document(collection_name: str, condition_description: str) -> dict:
    validated_input = DeleteDocumentInput(collection_name=collection_name, condition_description=condition_description)
    database = client["mcp_mongo_connector"]
    collection = database[validated_input.collection_name]
    schema_info = {"collection": validated_input.collection_name,
                   "fields": COLLECTION_SCHEMAS.get(validated_input.collection_name, {})}
    mongo_filter = translate_to_mongodb_query(user_request=validated_input.condition_description, schema_info=schema_info)
    result = collection.delete_many(mongo_filter)
    return {"deleted_count": result.deleted_count}