CREATE OR REPLACE TABLE bronze.raw_${table_name} AS
SELECT *, 
       CURRENT_TIMESTAMP AS ingestion_time,
       '${run_id}' AS run_id,
       'postgresql' AS data_source
FROM final_df;