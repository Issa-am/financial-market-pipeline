# Financial Market Data Pipeline

An end-to-end data engineering pipeline that ingests real-time stock market data, transforms it through a modern cloud data stack, and serves analytics-ready tables — fully automated and orchestrated.

## Architecture

```
Alpha Vantage API → AWS S3 (raw) → Databricks (PySpark) → AWS S3 (clean) → Snowflake → dbt → Analytics
```

## Tech Stack

| Layer | Tool |
|---|---|
| Ingestion | Python, boto3, Alpha Vantage API |
| Cloud Storage | AWS S3 (Parquet format) |
| Transformation | Databricks, PySpark, pandas |
| Data Warehouse | Snowflake |
| Data Modeling | dbt (staging + facts models) |
| Orchestration | Apache Airflow (Docker) |
| CI/CD | GitHub Actions |

## Pipeline Phases

### Phase 1 — Ingestion
Python script pulls daily stock data for 23 symbols (AAPL, MSFT, GOOGL, TSLA, NVDA...) from Alpha Vantage API and saves as Parquet files to AWS S3 `raw/stocks/` folder.

### Phase 2 — Transformation (Databricks)
PySpark notebook reads all 23 Parquet files from S3, combines into a single DataFrame (2,300 rows), adds calculated columns (daily_change, daily_change_pct, price_range, ingested_at), removes duplicates, and saves clean data back to S3 `clean/stocks/`.

### Phase 3 — Data Warehouse (Snowflake)
External stage connects Snowflake to S3. COPY INTO command loads 2,300 rows into `stocks_raw` table inside `financial_market_db.raw_data` schema.

### Phase 4 — Data Modeling (dbt)
Two dbt models transform the raw data:
- `stg_stocks` — staging model that cleans data types and filters invalid rows
- `fct_stocks` — facts model that aggregates 100 days of data per stock symbol (avg price, volume, best/worst day)

### Phase 5 — Orchestration (Airflow)
DAG `financial_market_pipeline` orchestrates the full pipeline daily at 6am:
1. `ingest_stock_data` — runs ingestion script
2. `run_dbt_models` — executes dbt transformations
3. `run_dbt_tests` — validates data quality

### Phase 6 — CI/CD (GitHub Actions)
Every push to main branch automatically triggers dbt validation against Snowflake using GitHub Actions. Secrets stored securely as GitHub repository secrets.

## Data

- **23 stock symbols** across tech, finance, and energy sectors
- **2,300 rows** of daily OHLCV data (100 days per symbol)
- **11 columns** including calculated metrics

## Known Issues and Fixes

## Challenges and Solutions

**1. Pandas date format incompatible with Snowflake**
Pandas stores datetime columns as nanoseconds since epoch in Parquet format. Snowflake could not parse these values and returned "Invalid date" for all rows.
Fix: Converted dates to strings using `.dt.strftime('%Y-%m-%d')` before saving to Parquet. dbt staging model then casts the string back to DATE type using `::DATE`.

**2. Snowflake COPY INTO date type mismatch**
Initial table defined date column as DATE type. Parquet nanosecond values could not be cast directly.
Fix: Changed column type to TIMESTAMP to accept the raw values, then handled type casting in dbt.

**3. CI/CD workflow failed on first run**
GitHub Actions could not connect to Snowflake because credentials were not available on GitHub's server.
Fix: Added Snowflake credentials as encrypted GitHub repository secrets and updated profiles.yml to read from environment variables using env_var().

**4. Airflow tasks failed in Docker**
DAG tasks failed because the Docker container does not have Python scripts or dbt installed inside it.
Note: In production, an Airflow Docker image would be built with all dependencies pre-installed. For this portfolio project, the DAG code and pipeline architecture are correct.

**5. dbt PATH issue on Windows**
Running dbt directly on Windows PowerShell failed because Anaconda Scripts folder was not in PATH.
Fix: Used full path to run all dbt commands.

## Setup

### Prerequisites
- Python 3.11+
- AWS account with S3 access
- Snowflake account
- Databricks account
- dbt-snowflake installed

### Environment Variables
```
DBT_SNOWFLAKE_ACCOUNT=your_account
DBT_SNOWFLAKE_USER=your_username
DBT_SNOWFLAKE_PASSWORD=your_password
```

### Run Pipeline
```bash
# Ingestion
python ingestion/fetch_stock_data.py

# dbt transformation
cd financial_market_dbt
dbt run
dbt test
```

## Author
Issa Amjadi | [GitHub](https://github.com/Issa-am)
