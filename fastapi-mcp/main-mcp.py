from fastapi_mcp import FastApiMCP
from main import app
import uvicorn

mcp = FastApiMCP(
    app,
    name="Inventory MCP Server",
    description="MCP server for managing inventory items"
)

mcp.mount()

if __name__ == "__main__":
    uvicorn.run("main-mcp:app", host="127.0.0.1", port=8000, reload=True)