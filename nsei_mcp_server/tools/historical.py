import pandas as pd
from typing import Dict
from mcp.server.fastmcp import FastMCP
from nsei_mcp_server.services.nse_downloader import get_data_for_date_range


def register_tool(mcp: FastMCP):
    @mcp.tool()
    async def get_historical_data(symbol: str, start_date: str, end_date: str) -> Dict:

        # getting the main data to work on
        df = get_data_for_date_range(start_date, (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days + 1)

        if df is None or df.empty:
            return {"No data available for the given range"}

        # filtering rows for the requested symbol
        filtered = df[df["SYMBOL"].str.upper() == symbol.upper()]

        if filtered.empty:
            return {"No records found for the symbol"}

        # defining the column names for futurechanges
        column_mapping = {
            "TIMESTAMP": "Date",
            "OPEN_PRICE": "Open",
            "HIGH_PRICE": "High",
            "LOW_PRICE": "Low",
            "CLOSE_PRICE": "Close",
            "TOTTRDQTY": "Volume"
        }

        # this only keeps the columns that are actually present, works like a check for missing columns
        available_cols = [col for col in column_mapping.keys() if col in filtered.columns]

        # renaming the avilable columns
        final_df = filtered[available_cols].rename(columns=column_mapping)

        #converting toa list of dicts
        historical_records = final_df.to_dict(orient="records")

        return {"symbol": symbol.upper(), "start_date": start_date, "end_date": end_date, "historical_data": historical_records}
