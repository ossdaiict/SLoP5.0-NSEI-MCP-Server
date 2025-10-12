# TODO: implement a get_market_summary tool
# accept date as a parameter
# calculate the sum of the  TotalTradingVolume (Total Trading Volume) and TotalTradingValue (Total Traded Value) columns
# return a dictionary with results

"""
USING A SAMPLE DATA VALUES TO COMPLETE THIS ISSUE
"""

from mcp.server.fastmcp import FastMCP
import pandas as pd
from typing import Dict

def register_tool(mcp: FastMCP):
    @mcp.tool()
    async def get_market_summary(date: str) -> Dict:
        """
        Gets a high-level market summary for a given date.
        Returns total trading volume and total trading value.
        """

        # we can replace this sample data with actual values when we pass
        data = pd.DataFrame([
            {"Symbol": "HDFCBANK", "TotalTradingVolume": 1850000, "TotalTradingValue": 3100000000},
            {"Symbol": "ASIANPAINT", "TotalTradingVolume": 920000, "TotalTradingValue": 2900000000},
            {"Symbol": "ITC", "TotalTradingVolume": 2400000, "TotalTradingValue": 1450000000},
        ])

        # Perform addition
        total_volume = data["TotalTradingVolume"].sum()
        total_value = data["TotalTradingValue"].sum()

        return {
            "date": date,
            "total_volume": int(total_volume),
            "total_value": float(total_value)
        }
