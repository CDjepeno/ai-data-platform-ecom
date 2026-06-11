from datetime import datetime

from etl_ecom.factory.pipeline_factory import PipelineFactory


def main() -> None:
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    PipelineFactory.create().execute(run_id)


if __name__ == "__main__":
    main()
