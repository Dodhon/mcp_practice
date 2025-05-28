# Practice FastAPI

A simple FastAPI application for practicing MCP transformation.

## Features

- CRUD operations for items
- Search functionality
- Health check endpoint
- Pydantic models for data validation

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

3. Visit `http://localhost:8000/docs` for interactive API documentation.

## API Endpoints

- `GET /` - Welcome message
- `GET /items` - Get all items
- `GET /items/{item_id}` - Get specific item
- `POST /items` - Create new item
- `PUT /items/{item_id}` - Update item
- `DELETE /items/{item_id}` - Delete item
- `GET /items/search/{query}` - Search items
- `GET /health` - Health check

## Sample Data

The API starts with 3 sample items (laptop, mouse, keyboard) for testing. 