from mcp.server.fastmcp import FastMCP
from typing import Dict
import pandas as pd

# Importing the existing data fetching function
from nsei_mcp_server.services.nse_downloader import get_data_for_date_range


def register_tool(mcp: FastMCP):
    @mcp.tool()
    async def get_trades(date: str, ndays: int = 1, symbol: str = None) -> Dict:

        if ndays < 1:
            return {"error": "Number of days (ndays) must be at least 1."}

        # getting the data
        df = get_data_for_date_range(date, ndays)
        if df is None or df.empty:
            return {"error": "No data available for the given date range."}

        #checcking data for the requested symbol
        if symbol:
            df = df[df["SYMBOL"].str.upper() == symbol.upper()]
            if df.empty:
                return {"error": f"No records found for symbol '{symbol}'."}

        #summarizing the data
        required_columns = ["SYMBOL", "TOTTRDQTY", "TOTTRDVAL", "OPEN_PRICE", "CLOSE_PRICE"]
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            return {"error": f"Missing columns in data: {missing_cols}"}

        summary = (
            df.groupby("SYMBOL").agg(
                total_volume=("TOTTRDQTY", "sum"),
                total_value=("TOTTRDVAL", "sum"),
                open_price=("OPEN_PRICE", "first"),
                close_price=("CLOSE_PRICE", "last")
            )
            .reset_index()
        )

        #convert to get a dictionary for proper return format
        trades_summary = summary.to_dict(orient="records")

        return {
            "start_date": date,
            "days": ndays,
            "symbol": symbol.upper() if symbol else None,
            "trade_summary": trades_summary
        }
