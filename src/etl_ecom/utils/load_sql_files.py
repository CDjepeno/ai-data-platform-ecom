from pathlib import Path

from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)


def load_sql_files(directory: str) -> dict[str, str]:
    path = Path(directory)
    logger.info(f"🔍 Recherche SQL dans: {path.resolve()}") 

    if not path.exists():
        logger.warning(f"⚠️  Dossier SQL introuvable: {directory}")
        return {}

    queries = {}

    for sql_file in sorted(path.glob("**/*.sql")):  # ← changement ici
        try:
            with open(sql_file, "r", encoding="utf-8") as f:
                query = f.read().strip()

            # Optionnel : clé avec chemin relatif pour éviter les collisions de noms
            relative_key = sql_file.relative_to(path).with_suffix('')
            queries[str(relative_key)] = query
            logger.info(f"📄 Chargé: {sql_file.relative_to(path)}")

        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement de {sql_file.name}: {e}")

    return queries


def load_sql_file(filepath: Path) -> str | None:
    """
    Charge un fichier SQL depuis un chemin donné.

    Args:
        filepath: Chemin complet vers le fichier .sql (ex: 'src/etl_ecom/ingestion/sql/watermark.sql')

    Returns:
        Contenu du fichier (string) ou None si fichier introuvable
    """
    path = filepath

    if not path.exists():
        logger.warning(f"⚠️  Fichier introuvable: {path}")
        return None

    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()