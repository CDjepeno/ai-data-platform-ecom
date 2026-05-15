def warehouse_initialized(conn) -> bool:
    try:
        result = conn.execute("""
            SHOW TABLES FROM iceberg.mart
        """).fetchall()

        return len(result) > 0

    except Exception:
        return False