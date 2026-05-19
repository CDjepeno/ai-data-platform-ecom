from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool

from transformations.run_dbt_build import run_dbt_build

router = APIRouter()


@router.post("/build-dbt")
async def build_dbt():

    await run_in_threadpool(run_dbt_build)

    return {"response": "DBT build completed successfully"}