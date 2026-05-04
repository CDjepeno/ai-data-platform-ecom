from sqlalchemy import Engine



def build_query(table: str, limit: int = 0) -> str:
    query = f"SELECT * FROM {table}"
    
    if limit:
        query += f" LIMIT {limit}"
    
    return query + ";"