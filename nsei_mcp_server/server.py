from mcp.server.fastmcp import FastMCP

# TODO: Import the tool registration functions from the tools/ directory

# Initialize FastMCP server
mcp = FastMCP("nsei_mcp_server")

print("Registering tools...")
# TODO: Register all the tools here by calling their registration functions
# Example: trades.register_tool(mcp)


if __name__ == "__main__":
    print("Starting NSEI MCP Server...")
    mcp.run(transport='stdio')