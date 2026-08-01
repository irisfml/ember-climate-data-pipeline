import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Data Source Configurations
DATA_URL = os.getenv(
    "EMBER_DATA_URL",
    "https://raw.githubusercontent.com/ember-climate/global-electricity-data/main/data/monthly_full_release_long_format.csv"
)

# Database Configurations
DB_PATH = os.getenv("DUCKDB_PATH", "data/ember_climate.db")
RAW_TABLE_NAME = "raw_electricity_generation"

# Target Country Filter
TARGET_COUNTRY = "Brazil"