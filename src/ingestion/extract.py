import os
import pandas as pd
import duckdb

DB_PATH = "data/ember_climate.db"
# Direct URL to official Ember yearly electricity generation dataset
EMBER_DATA_URL = "https://files.ember-energy.org/public-downloads/generation/outputs/release_generation_yearly_global.csv"

def fetch_ember_data_from_url():
    """
    Downloads official global yearly electricity dataset directly from Ember file storage.
    Filters the dataset for Brazil to maintain an optimized staging layer.
    """
    print(f"Downloading official Ember dataset directly from storage...")
    
    # Pandas reads the CSV directly from the HTTP URL
    df = pd.read_csv(EMBER_DATA_URL)
    
    # Filter for Brazil to keep local staging light for development
    df_brazil = df[df["Area"] == "Brazil"].copy()
    
    print(f"Successfully downloaded {len(df_brazil)} rows for Brazil.")
    return df_brazil

def save_raw_to_duckdb(df):
    """
    Saves raw records directly into a DuckDB staging table following ELT architecture.
    """
    if df.empty:
        print("No records to save.")
        return

    # Ensure local data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Connect to DuckDB (creates local file if missing)
    conn = duckdb.connect(DB_PATH)
    
    # Register DataFrame and overwrite raw staging table
    conn.register("df_view", df)
    conn.execute("CREATE OR REPLACE TABLE raw_electricity_generation AS SELECT * FROM df_view;")
    
    # Validate count
    count = conn.execute("SELECT COUNT(*) FROM raw_electricity_generation;").fetchone()[0]
    print(f"Raw data successfully loaded into DuckDB ({DB_PATH}). Total rows in staging: {count}")
    
    conn.close()

if __name__ == "__main__":
    try:
        raw_df = fetch_ember_data_from_url()
        save_raw_to_duckdb(raw_df)
    except Exception as e:
        print(f"Extraction Pipeline Error: {e}")