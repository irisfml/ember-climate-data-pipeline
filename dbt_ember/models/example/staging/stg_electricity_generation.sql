/*
  Staging model for Ember yearly electricity generation raw data.
  Standardizes column names, casts data types, and filters relevant metrics.
*/

WITH raw_data AS (
    SELECT * 
    FROM {{ source('main', 'raw_electricity_generation') }}
)

SELECT
    "Area" AS country_name,
    "ISO3" AS country_code,
    CAST("Year" AS INTEGER) AS reporting_year,
    "Variable" AS energy_source,
    "Unit" AS metric_unit,
    CAST("Value" AS DOUBLE) AS metric_value
FROM raw_data
WHERE "Value" IS NOT NULL