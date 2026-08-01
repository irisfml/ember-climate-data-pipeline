import os
import pandas as pd
import requests
import duckdb
from .config import DATA_URL, DB_PATH, RAW_TABLE_NAME, TARGET_COUNTRY
from .logger import setup_logger

logger = setup_logger("extract_module")

def fetch_data(url: str) -> pd.DataFrame:
    """
    Fetches raw CSV data. Uses a local fallback if the web request fails or is blocked.
    """
    logger.info(f"Attempting connection to API endpoint: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        logger.info("Data fetched successfully from source. Parsing CSV payload...")
        return pd.read_csv(pd.io.common.BytesIO(response.content))
    except Exception as e:
        logger.warning(f"Web source unavailable or blocked ({e}). Activating resilience fallback...")
        local_path = "data/raw_ember_data.csv"
        
        if os.path.exists(local_path):
            logger.info(f"Successfully loaded dataset from local fallback: {local_path}")
            return pd.read_csv(local_path)
        else:
            logger.error("Critical: Local fallback file not found in 'data/' folder.")
            raise

def load_to_duckdb(df: pd.DataFrame, db_path: str, table_name: str) -> None:
    """
    Loads filtered DataFrame into DuckDB raw table idempotently.
    Dynamically identifies country column ('Country / Area', 'Area', 'Country / Territory', or 'Country').
    """
    logger.info(f"Filtering dataset for target country: {TARGET_COUNTRY}")
    
    # Identify country column dynamically based on payload schema
    possible_country_cols = ['Country / Area', 'Area', 'Country / Territory', 'Country', 'country', 'area']
    country_col = None
    
    for col in possible_country_cols:
        if col in df.columns:
            country_col = col
            break
            
    if not country_col:
        raise KeyError(f"Could not find country column in DataFrame. Available columns: {list(df.columns)}")
    
    logger.info(f"Using country column: '{country_col}'")
    df_filtered = df[df[country_col] == TARGET_COUNTRY].copy()
    
    if df_filtered.empty:
        logger.warning(f"No records found for country: {TARGET_COUNTRY}")
        return

    logger.info(f"Connecting to DuckDB target database at: {db_path}")
    try:
        conn = duckdb.connect(db_path)
        conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df_filtered")
        
        record_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        logger.info(f"Successfully loaded {record_count} records into '{table_name}' table.")
        conn.close()
    except duckdb.Error as e:
        logger.error(f"Database operation failed: {e}")
        raise