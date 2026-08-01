from .config import DATA_URL, DB_PATH, RAW_TABLE_NAME
from .extract import fetch_data, load_to_duckdb
from .logger import setup_logger

logger = setup_logger("main_pipeline")

def run_pipeline():
    logger.info("Starting Ingestion Pipeline Execution...")
    try:
        raw_df = fetch_data(DATA_URL)
        load_to_duckdb(raw_df, DB_PATH, RAW_TABLE_NAME)
        logger.info("Ingestion Pipeline Completed Successfully!")
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise

if __name__ == "__main__":
    run_pipeline()