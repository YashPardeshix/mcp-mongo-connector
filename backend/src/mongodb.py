import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client["mcp_db"]


def execute_query(collection_name: str, query_filter: dict) -> list[dict]:
    """Executes a query filter against a collection and returns JSON-safe documents."""
    collection = db[collection_name]
    cursor = collection.find(query_filter)

    results = []
    for doc in cursor:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        results.append(doc)

    return results


def insert_doc(collection_name: str, document: dict) -> str:
    """Inserts a single document into MongoDB and returns the inserted ID as a string."""
    collection = db[collection_name]
    result = collection.insert_one(document)
    return str(result.inserted_id)
