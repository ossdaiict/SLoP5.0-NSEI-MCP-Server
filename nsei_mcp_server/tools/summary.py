from mcp.server.fastmcp import FastMCP
from typing import Dict
from nsei_mcp_server.services.nse_downloader import _download_bhav_copy
import pandas as pd

def register_tool(mcp: FastMCP):
    @mcp.tool()
    async def get_market_summary(date: str):
        """
        Gets a high-level market summary for a given date.
        Returns total trading volume and total trading value.
        """

        # Fetch actual data for the date
        data = _download_bhav_copy(date)

        # Check data
        if data is None or data.empty:
            return {"error": "No data available for the given date."}

        # Compute totals from actual Bhav Copy columns
        total_volume = data["TtlTradgVol"].sum()
        total_value = data["TtlTrfVal"].sum()

        # Return formatted summary
        return {
            "date": date, "total_volume": int(total_volume), "total_value": float(total_value)
        }
