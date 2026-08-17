import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client["mcp_db"]


def execute_query(collection_name: str, query_filter: dict) -> list[dict]:
    """Executes a query filter against a MongoDB collection and returns matching documents."""
    collection = db[collection_name]
    cursor = collection.find(query_filter)

    results = []
    for doc in cursor:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        results.append(doc)

    return results

if __name__ == "__main__":
    print("Testing MongoDB Atlas Connection...")

    products_col = db["products"]
    products_col.insert_one(
        {
            "title": "Nike Air Running Shoes",
            "price": 85,
            "category": "shoes",
            "in_stock": True,
        }
    )
    print("Inserted test document into MongoDB Atlas!")

    test_filter = {"category": "shoes", "price": {"$lt": 100}}
    documents = execute_query("products", test_filter)

    print(f"\nFound {len(documents)} document(s) in MongoDB Atlas:")
    print(documents)