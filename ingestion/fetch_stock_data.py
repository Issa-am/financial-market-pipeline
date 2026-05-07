"""
Financial Market Pipeline - Stock Data Ingestion
Pulls daily stock data for 25 symbols from Alpha Vantage API
and saves to AWS S3 as Parquet files.
Author: Issa Amjadi
"""

import requests
import pandas as pd
import boto3
from datetime import datetime
import time
import os

# --- CONFIG ---
API_KEY = "SLELCF9M0KNGDCAW"
S3_BUCKET = "financial-market-pipeline-issa"
S3_PREFIX = "raw/stocks"

SYMBOLS = [
    "IBM", "AAPL", "MSFT", "GOOGL", "AMZN",
    "TSLA", "META", "NVDA", "JPM", "BAC",
    "WFC", "GS", "MS", "C", "AXP",
    "XOM", "CVX", "COP", "SLB", "EOG",
    "JNJ", "PFE", "UNH", "ABT", "MRK"
]

def fetch_stock_data(symbol: str) -> pd.DataFrame:
    """Pull daily stock data from Alpha Vantage API."""
    url = (
        f"https://www.alphavantage.co/query"
        f"?function=TIME_SERIES_DAILY"
        f"&symbol={symbol}"
        f"&apikey={API_KEY}"
        f"&outputsize=compact"
    )

    print(f"Fetching data for {symbol}...")
    response = requests.get(url)
    data = response.json()

    if "Time Series (Daily)" not in data:
        print(f"WARNING: No data for {symbol} — skipping")
        return None

    time_series = data["Time Series (Daily)"]

    records = []
    for date, values in time_series.items():
        records.append({
            "symbol": symbol,
            "date": date,
            "open": float(values["1. open"]),
            "high": float(values["2. high"]),
            "low": float(values["3. low"]),
            "close": float(values["4. close"]),
            "volume": int(values["5. volume"])
        })

    df = pd.DataFrame(records)
    print(f"Fetched {len(df)} rows for {symbol}")
    return df

def save_to_s3(df: pd.DataFrame, symbol: str):
    """Save DataFrame to S3 as Parquet file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{symbol}_{timestamp}.parquet"
    tmp_path = f"/tmp/{filename}"
    s3_key = f"{S3_PREFIX}/{symbol}/{filename}"

    df.to_parquet(tmp_path, index=False)

    s3 = boto3.client("s3")
    s3.upload_file(tmp_path, S3_BUCKET, s3_key)
    print(f"Uploaded to s3://{S3_BUCKET}/{s3_key}")

def run_ingestion():
    """Loop through all symbols and ingest data."""
    print(f"Starting ingestion for {len(SYMBOLS)} symbols...")
    success = 0
    failed = 0

    for symbol in SYMBOLS:
        df = fetch_stock_data(symbol)
        if df is not None:
            save_to_s3(df, symbol)
            success += 1
        else:
            failed += 1
        time.sleep(12)  # API allows 5 requests/minute

    print(f"\nDone! Success: {success} | Failed: {failed}")

if __name__ == "__main__":
    run_ingestion()