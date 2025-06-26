# app/api/deps.py

from app.services.mcp_client import MCPClient

def get_mcp_client() -> MCPClient:
    """
    Dependency that provides an MCPClient instance.
    FastAPI will call this function and inject the client into routes.
    """
    return MCPClient()
