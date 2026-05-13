import trino

from etl_ecom.db.engine import get_trino_connection

def execute_query(sql: str):

    conn = get_trino_connection()

    cursor = conn.cursor()

    cursor.execute(sql)

    rows = cursor.fetchall()

    columns = [col[0] for col in cursor.description]

    results = [
        dict(zip(columns, row))
        for row in rows
    ]

    return results