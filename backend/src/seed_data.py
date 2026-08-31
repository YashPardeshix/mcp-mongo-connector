from mongodb import client

database = client["mcp_mongo_connector"]

products = [
    {"title": "Nike Air Max", "price": 4999, "category": "shoes", "brand": "Nike", "color": "blue", "in_stock": True},
    {"title": "Nike Revolution", "price": 2999, "category": "shoes", "brand": "Nike", "color": "black", "in_stock": True},
    {"title": "Adidas Ultraboost", "price": 8999, "category": "shoes", "brand": "Adidas", "color": "white", "in_stock": False},
    {"title": "Puma RS-X", "price": 3499, "category": "shoes", "brand": "Puma", "color": "red", "in_stock": True},
    {"title": "Nike Hoodie", "price": 1999, "category": "clothing", "brand": "Nike", "color": "grey", "in_stock": True},
    {"title": "Adidas Track Pants", "price": 1499, "category": "clothing", "brand": "Adidas", "color": "black", "in_stock": True},
    {"title": "Puma Cap", "price": 599, "category": "accessories", "brand": "Puma", "color": "blue", "in_stock": False},
    {"title": "Nike Backpack", "price": 2499, "category": "accessories", "brand": "Nike", "color": "black", "in_stock": True},
]

users = [
    {"name": "Dhap Rajput", "email": "dhap@example.com", "role": "admin", "age": 19},
    {"name": "Shreyas Sonawane", "email": "shreyas@example.com", "role": "customer", "age": 26},
    {"name": "Tushar Mali", "email": "tushar@example.com", "role": "customer", "age": 26},
]

orders = [
    {"order_id": "ORD001", "user_email": "dhap@example.com", "total_amount": 4999, "status": "shipped"},
    {"order_id": "ORD002", "user_email": "shreyas@example.com", "total_amount": 2999, "status": "pending"},
    {"order_id": "ORD003", "user_email": "rushar@example.com", "total_amount": 1499, "status": "delivered"},
]

if __name__ == "__main__":
    database["products"].insert_many(products)
    database["users"].insert_many(users)
    database["orders"].insert_many(orders)
    print(f"Inserted {len(products)} products, {len(users)} users, {len(orders)} orders.")