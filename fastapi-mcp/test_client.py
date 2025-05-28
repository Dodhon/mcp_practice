import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
import json


def decode_tool_result(result):
    """Decode the tool result to a string"""
    try: 
        if type(result.content) == list:
            text_content = [item for item in result.content if item.type == "text"]
            return text_content[0].text if text_content else None
        elif type(result.content) == dict:
            text_content = [item for item in result.content.values() if item.type == "text"]
            return text_content[0].text if text_content else None
        elif type(result.content) == str:
            return result.content
        else:
            raise ValueError(f"Unsupported content type: {type(result.content)}")
    
    except Exception as e:
        print(f"tool response error: {e}")

async def test_mcp_tools():
    """Test your FastAPI MCP server tools"""
    
    print("Testing FastAPI MCP Server...")
    print("Server: http://127.0.0.1:8000/mcp")
    print("-" * 50)
    
    try:
        async with sse_client("http://127.0.0.1:8000/mcp") as (read, write):
            async with ClientSession(read, write) as session:
                
                await session.initialize()
                print("Connected to MCP server")
                
                tools_response = await session.list_tools()
                print(f"Found {len(tools_response.tools)} tools")
                
                for tool in tools_response.tools:
                    print(f"\nTesting: {tool.name}")
                    try:
                        # Provide proper arguments for each tool
                        if tool.name == "welcome":
                            result = await session.call_tool(tool.name, {})
                        elif tool.name == "list_items":
                            result = await session.call_tool(tool.name, {})
                        elif tool.name == "create_item":
                            result = await session.call_tool(tool.name, {
                                "name": "Test Item",
                                "price": 19.99
                            })
                        elif tool.name == "get_item":
                            result = await session.call_tool(tool.name, {"item_id": 1})
                        elif tool.name == "update_item":
                            result = await session.call_tool(tool.name, {
                                "item_id": 1,
                                "name": "Updated Item",
                                "price": 25.99
                            })
                        elif tool.name == "delete_item":
                            print("Skipped (destructive)")
                            continue
                        elif tool.name == "search_items":
                            result = await session.call_tool(tool.name, {"query": "test"})
                        elif tool.name == "health_check":
                            result = await session.call_tool(tool.name, {})
                        else:
                            result = await session.call_tool(tool.name, {})
                        
                        print(f"Success: {decode_tool_result(result)}")
                    except Exception as e:
                        print(f"Failed: {e}")
                        
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())