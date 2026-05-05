from pathlib import Path
from typing import cast

import yaml

from etl_ecom.types.typing import IngestionConfig


def load_config_table() -> IngestionConfig:
    # 📍 dossier du fichier actuel (config/)
    base_dir = Path(__file__).resolve().parent
    print(base_dir)
    # 📄 chemin vers ingestion.yml
    config_path = base_dir / "ingestion_config.yml"

    if not config_path.exists():
        raise FileNotFoundError(f"❌ Config file not found: {config_path}")

    with open(config_path, "r") as f:
        return cast(IngestionConfig, yaml.safe_load(f))


CONFIG = load_config_table()
TABLE_CONFIG = CONFIG["tables"]
