from mcp.server.fastmcp import FastMCP
from typing import Dict

# TODO: Import the data fetching function from the services directory

def register_tool(mcp: FastMCP):
    @mcp.tool("get_top_movers")
    async def get_top_movers(date: str, ndays: int = 1) -> Dict:
        """
        Get top market movers from the NSE for a given period.
        """
        if ndays < 1:
            return {"error": "Number of days (ndays) must be at least 1."}
        # TODO: Implement the logic for the get_top_movers tool.
        # 1. Fetch data using the service.
        # 2. Calculate percentage changes.
        # 3. Find the top N gainers and losers.
        # 4. Return the formatted result.
        raise NotImplementedError
