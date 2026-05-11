from pathlib import Path
import subprocess

from etl_ecom.utils.logger import get_logger


logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent



def run_dbt_build():

    logger.info("🚀 Running dbt build...")

    result = subprocess.run(
        [
            "poetry",
            "run",
            "dbt",
            "build"
        ],
        cwd=BASE_DIR,
        capture_output=True,
        text=True
    )

    logger.info(result.stdout)

    if result.returncode != 0:
        logger.error(result.stderr)
        raise Exception("❌ dbt build failed")

    logger.info("✅ dbt build completed")