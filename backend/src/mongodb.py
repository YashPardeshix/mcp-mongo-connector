import os

from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI is not set in the .env file.")


client = MongoClient(MONGODB_URI)


def test_connection():
    client.admin.command("ping")
    print("MongoDB connection successful!")

    database = client["mcp_mongo_connector"]
    collection = database["products"]

    test_document = {
        "title": "Test Nike Shoe",
        "price": 4999,
        "category": "shoes",
        "brand": "Nike",
        "color": "blue",
        "in_stock": True,
    }

    result = collection.insert_one(test_document)

    print(f"Inserted document ID: {result.inserted_id}")

    inserted_document = collection.find_one(
        {"_id": result.inserted_id}
    )

    print("Retrieved document:")
    print(inserted_document)


if __name__ == "__main__":
    test_connection()