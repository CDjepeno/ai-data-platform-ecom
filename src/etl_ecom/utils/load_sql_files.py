from pathlib import Path

from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)


def load_sql_files(directory: str) -> dict[str, str]:
    """
    Charge tous les fichiers SQL d'un dossier.

    Args:
        directory: Chemin vers le dossier contenant les fichiers .sql

    Returns:
        Dictionnaire {nom_fichier_sans_extension: contenu_sql}
    """
    path = Path(directory)

    if not path.exists():
        logger.warning(f"⚠️  Dossier SQL introuvable: {directory}")
        return {}

    queries = {}

    for sql_file in sorted(path.glob("*.sql")):
        try:
            with open(sql_file, "r", encoding="utf-8") as f:
                query = f.read().strip()

            queries[sql_file.stem] = query
            logger.info(f"📄 Chargé: {sql_file.name}")

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