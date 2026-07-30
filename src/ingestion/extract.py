import os
import requests
import pandas as pd
import duckdb
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

EMBER_API_KEY = os.getenv("EMBER_API_KEY")
DB_PATH = "data/ember_climate.db"

def fetch_ember_data(entity_code="BRA", series_id="gen", year_from=2015):
    """
    Fetches electricity generation and emissions data from the Ember API.
    
    :param entity_code: ISO 3-letter country code (e.g., 'BRA' for Brazil, 'USA', 'DEU')
    :param series_id: Metrics series ('gen' for generation, 'emissions' for carbon emissions)
    :param year_from: Starting year for historical analysis
    """
    if not EMBER_API_KEY:
        raise ValueError("EMBER_API_KEY is not set in the environment variables.")

    url = "https://api.ember-climate.org/v1/electricity-generation/yearly"
    
    params = {
        "api_key": EMBER_API_KEY,
        "entity_code": entity_code,
        "start_date": year_from
    }
    
    print(f"Fetching Ember Climate data for entity: {entity_code}...")
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get("data", [])
        print(f"Successfully retrieved {len(results)} records.")
        return results
    else:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

def save_raw_to_duckdb(records):
    """
    Saves raw API records directly into a DuckDB raw staging table.
    """
    if not records:
        print("No records to save.")
        return

    # Convert raw JSON records to Pandas Dataframe
    df = pd.DataFrame(records)
    
    # Connect to DuckDB (creates the file if it doesn't exist)
    conn = duckdb.connect(DB_PATH)
    
    # Save raw records into a raw staging table (Replacing old staging for fresh loads)
    conn.execute("CREATE TABLE IF NOT EXISTS raw_electricity_generation AS SELECT * FROM df WHERE 1=0;")
    conn.register("df_view", df)
    conn.execute("CREATE OR REPLACE TABLE raw_electricity_generation AS SELECT * FROM df_view;")
    
    # Query count to verify insertion
    count = conn.execute("SELECT COUNT(*) FROM raw_electricity_generation;").fetchone()[0]
    print(f"Raw data successfully loaded into DuckDB. Total rows: {count}")
    
    conn.close()

if __name__ == "__main__":
    try:
        # Fetch data for Brazil as initial test case
        raw_data = fetch_ember_data(entity_code="BRA", year_from=2015)
        save_raw_to_duckdb(raw_data)
    except Exception as e:
        print(f"Extraction Pipeline Error: {e}")