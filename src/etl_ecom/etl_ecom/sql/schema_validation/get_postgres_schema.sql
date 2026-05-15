SELECT
    table_name,
    column_name,
    data_type
FROM postgres_db.information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
