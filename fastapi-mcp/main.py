from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from fastapi_mcp import FastApiMCP

app = FastAPI(title="Practice FastAPI", description="A simple fastapi app")

# Pydantic models
class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    in_stock: bool = True

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    in_stock: bool = True

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    in_stock: Optional[bool] = None

# In-memory storage
items_db: List[Item] = [
    Item(id=1, name="Laptop", description="Gaming laptop", price=999.99, in_stock=True),
    Item(id=2, name="Mouse", description="Wireless mouse", price=29.99, in_stock=True),
    Item(id=3, name="Keyboard", description="Mechanical keyboard", price=149.99, in_stock=False)
]

@app.get("/", operation_id="welcome")
async def root():
    """Get welcome message"""
    return {"message": "Welcome to Practice FastAPI"}

@app.get("/items", response_model=List[Item], operation_id="list_items")
async def get_items():
    """Get all items from inventory"""
    return items_db

@app.get("/items/{item_id}", response_model=Item, operation_id="get_item")
async def get_item(item_id: int):
    """Get a specific item by ID"""
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.post("/items", response_model=Item, operation_id="create_item")
async def create_item(item: ItemCreate):
    """Create a new item in inventory"""
    new_id = max([item.id for item in items_db], default=0) + 1
    new_item = Item(id=new_id, **item.dict())
    items_db.append(new_item)
    return new_item

@app.put("/items/{item_id}", response_model=Item, operation_id="update_item")
async def update_item(item_id: int, item_update: ItemUpdate):
    """Update an existing item"""
    for i, item in enumerate(items_db):
        if item.id == item_id:
            update_data = item_update.dict(exclude_unset=True)
            updated_item = item.copy(update=update_data)
            items_db[i] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/items/{item_id}", operation_id="delete_item")
async def delete_item(item_id: int):
    """Delete an item from inventory"""
    for i, item in enumerate(items_db):
        if item.id == item_id:
            deleted_item = items_db.pop(i)
            return {"message": f"Item '{deleted_item.name}' deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")

@app.get("/items/search/{query}", operation_id="search_items")
async def search_items(query: str):
    """Search items by name or description"""
    results = []
    for item in items_db:
        if (query.lower() in item.name.lower() or 
            (item.description and query.lower() in item.description.lower())):
            results.append(item)
    return results

@app.get("/health", operation_id="health_check")
async def health_check():
    """Check API health status"""
    return {"status": "healthy", "items_count": len(items_db)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 