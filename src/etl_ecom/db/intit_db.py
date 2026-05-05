from pathlib import Path


from sqlalchemy import text

from etl_ecom.db.engine import get_duckdb_connection


# Chemin absolu basé sur l'emplacement de ce fichier
BASE_SQL_DIR = Path(__file__).resolve().parent.parent  / "ingestion"

def run_sql_folder(con, folder):
    folder_path = BASE_SQL_DIR / folder
    for file in sorted(folder_path.rglob("*.sql")):
        print(f"📄 Exécution de {file.name}...")
        with open(file, 'r', encoding='utf-8') as f:
            sql = f.read().strip()
            if sql:
                con.execute(sql)  # Pas de text() pour DuckDB direct
                print(f"✅ {file.name} exécuté")


def init_db():
    engine = get_duckdb_connection()
    
    run_sql_folder(engine, "sql/metadata/ddl")
    
    engine.close()
        
if __name__ == "__main__":
    init_db()
