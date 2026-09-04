# MCP MongoDB Connector

A Model Context Protocol (MCP) server that lets an AI talk to a MongoDB database in plain English — no query syntax required on either side.

Instead of writing `db.products.find({price: {$lt: 5000}})`, you just say "find products under 5000." The server translates that into a real, validated MongoDB query, runs it, and hands the results back.

## Why this exists

MCP is becoming one of the standard ways AI models connect to external tools and data sources. Most people who "use" MCP just configure someone else's server. This project builds one from scratch — the server, the natural-language-to-query translation layer, and the validation in between — to actually understand how the protocol works under the hood.

## How it works

1. An AI (or the demo client) sends a natural-language request to one of five exposed MCP tools.
2. The tool pulls the relevant collection's schema and hands both the request and the schema to a translation layer.
3. The translation layer (an LLM call) converts the plain-English request into a structured MongoDB query or document.
4. That structured output is validated against a Pydantic schema before it ever touches the database — this step exists specifically to catch hallucinated fields, wrong types, and malformed queries before they can cause silent, wrong results.
5. PyMongo executes the validated operation against MongoDB Atlas.
6. The result is returned to the caller..

## Tools exposed

| Tool | What it does |
|---|---|
| `query-collection` | Finds documents matching a natural-language request |
| `insert-document` | Creates a new document from a natural-language description |
| `update-document` | Updates documents matching a natural-language condition |
| `delete-document` | Deletes documents matching a natural-language condition |
| `describe-schema` | Returns the field names and types for a given collection |

## Tech stack

- **Python** — server and translation layer
- **MCP SDK** — the real protocol implementation, not a wrapper
- **MongoDB Atlas** (free tier) — cloud-hosted database
- **PyMongo** — MongoDB driver
- **Pydantic** — validates every translated query/document before it reaches the database
- **NVIDIA NIM (Nemotron)** — the LLM used for translation

## Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:
```
MONGODB_URI=your_atlas_connection_string
NVIDIA_API_KEY=your_nvidia_api_key
```

Seed the demo data:
```bash
cd src
python3 seed_data.py
```

Run the server:
```bash
python3 mcp_tools.py
```

## Example queries that work

- "Find Nike shoes under 5000"
- "Find products cheaper than ₹1,000"
- "Find products costing more than ₹10,000"
- "Find blue Nike shoes that are in stock"
- "Show me shoes that are currently out of stock"
- "Add a red Puma sneaker costing 3499 that is in stock"
- "Change the price to 2999" (as an update, filtered by "the Puma product priced at 3499")
- "Delete the test Nike shoe priced at 4999"

## Known limitations

**Translator does literal extraction, not semantic inference.** If you ask for "a sneaker," the translator won't automatically map that to `category: "shoes"` — it only picks up fields and values you state explicitly. Asking for "a product in the shoes category" works correctly; relying on implied categories doesn't yet. This showed up in testing on both the insert and update paths and is a good next improvement — likely a one-line addition to the translation prompt telling it to infer category from common product-type words.

**Query-filter schema and collection schema are maintained separately.** `COLLECTION_SCHEMAS` (used to tell the translator what fields exist) and `MongoQueryFilter` (used to validate what comes back) are both hand-written and have to be kept in sync manually. Adding a field to one collection means updating both. A cleaner version of this project would generate the Pydantic model directly from the schema dictionary instead of duplicating the field list.

**Validation is currently built for `products`.** `MongoQueryFilter` and `MongoDocument` are shaped around the products collection's fields. Extending clean validation to `users` and `orders` would mean either generalizing these models or building one per collection.

## What I'd do differently

I'd generate the Pydantic validation models from the schema dictionary instead of writing both by hand — the schema-drift bug (a field existing in one but not the other) cost real debugging time that a single source of truth would have avoided entirely.