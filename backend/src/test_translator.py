from translator import translate_to_mongodb_query


TEST_SCHEMA = {
    "collection": "products",
    "fields": {
        "title": "string",
        "price": "number",
        "category": "string",
        "brand": "string",
        "color": "string",
        "in_stock": "boolean",
    },
}


TESTS = [
    ("Test 1 - Equality", "Find Nike products.", {"brand": "Nike"}),
    ("Test 2 - Less Than", "Find products cheaper than ₹1,000.",
     {"price": {"$lt": 1000}}),
    ("Test 3 - Greater Than", "Find products costing more than ₹10,000.",
     {"price": {"$gt": 10000}}),
    ("Test 4 - Multiple Conditions", "Find Nike products under ₹5,000.",
     {"brand": "Nike", "price": {"$lt": 5000}}),
    ("Test 5 - Boolean", "Find products that are currently out of stock.",
     {"in_stock": False}),
    ("Test 6 - Category", "Find all products in the shoes category.",
     {"category": "shoes"}),
    ("Test 7 - Four Conditions",
     "Find blue Nike shoes that are in stock.",
     {"brand": "Nike", "category": "shoes",
      "color": "blue", "in_stock": True}),
    ("Test 8 - Natural Language Variation",
     "Show me the cheaper Nike shoes, below ₹5,000.",
     {"brand": "Nike", "category": "shoes",
      "price": {"$lt": 5000}}),
    ("Test 9 - Boolean + Category",
     "Show me shoes that are currently out of stock.",
     {"category": "shoes", "in_stock": False}),
    ("Test 10 - Complex",
     "Find blue Nike shoes under ₹3,000 that are currently in stock.",
     {"brand": "Nike", "category": "shoes", "color": "blue",
      "price": {"$lt": 3000}, "in_stock": True}),
]


def run_test(name, request, expected):
    print(f"\n{name}")
    print(f"Request: {request}")

    try:
        actual = translate_to_mongodb_query(
            user_request=request,
            schema_info=TEST_SCHEMA,
        )

        if actual == expected:
            print("PASS")
            return True

        print("FAIL")
        print("Expected:", expected)
        print("Actual:  ", actual)
        return False

    except Exception as exc:
        print("FAIL")
        print(f"Error: {exc}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("TRANSLATOR TEST SUITE")
    print("=" * 60)

    passed = 0

    for test in TESTS:
        if run_test(*test):
            passed += 1

    total = len(TESTS)

    print("\n" + "=" * 60)
    print(f"RESULT: {passed}/{total} tests passed")
    print("=" * 60)

    if passed != total:
        raise SystemExit(1)