# Semantic Layer — Build Sequence Diagram

Triggered at the end of each ETL pipeline cycle, after all Iceberg tables are loaded.

```mermaid
sequenceDiagram
    autonumber

    participant UC as RunPipelineUseCase<br/>(etl_ecom)
    participant Adapter as HttpSemanticLayerAdapter<br/>(etl_ecom)
    participant SL as SemanticLayer API<br/>(:8001 FastAPI)
    participant DBT as dbt subprocess
    participant Trino as Trino<br/>(:8080)
    participant Nessie as Nessie<br/>(:19120)
    participant Minio as MinIO / Iceberg<br/>(:9000)
    participant Qdrant as Qdrant<br/>(:6333)
    participant OpenAI as OpenAI<br/>(embed API)

    Note over UC: ETL cycle complete — all Iceberg tables loaded

    %% ── Phase 1 : dbt build ───────────────────────────────────────────────────
    rect rgb(230, 240, 255)
        Note over UC,Minio: Phase 1 — dbt build

        UC->>Adapter: build_dbt()
        Adapter->>SL: POST /build-dbt (httpx, timeout=300s)

        SL->>DBT: subprocess: dbt build
        Note over DBT: runs all models:<br/>raw → silver → mart<br/>+ MetricFlow semantic layer

        loop for each dbt model
            DBT->>Trino: SQL query (model compilation)
            Trino->>Nessie: resolve Iceberg table location
            Nessie-->>Trino: s3://ecom-etl/warehouse/raw/...
            Trino->>Minio: read Parquet files (Iceberg scan)
            Minio-->>Trino: columnar data
            Trino-->>DBT: result set
            DBT->>Minio: write transformed Parquet (silver/mart)
        end

        DBT-->>SL: returncode=0, stdout
        SL-->>Adapter: 200 {"response": "DBT build completed successfully"}
        Adapter-->>UC: build_dbt() returns (logs duration)
    end

    %% ── Phase 2 : semantic indexing ───────────────────────────────────────────
    rect rgb(230, 255, 235)
        Note over UC,Qdrant: Phase 2 — semantic indexing

        UC->>Adapter: index()
        Adapter->>SL: POST /index (httpx, timeout=300s)

        SL->>Qdrant: recreate_collection()<br/>(drops old vectors, creates fresh collection)

        Note over SL: SemanticModelsIndexer — reads semantic_models/*.yml

        loop for each semantic model .yml
            SL->>OpenAI: embed(model_name + measures + dimensions text)
            OpenAI-->>SL: float[1536] vector
            SL->>Qdrant: insert_embedding(point_id, vector, payload={type:"semantic_model"})
        end

        Note over SL: MetricIndexer — reads metrics/*.yml

        loop for each metric .yml
            SL->>OpenAI: embed(metric_name + description + type + measure text)
            OpenAI-->>SL: float[1536] vector
            SL->>Qdrant: insert_embedding(point_id, vector, payload={type:"metric"})
        end

        SL-->>Adapter: 200 {"status": "ok"}
        Adapter-->>UC: index() returns (logs duration)
    end

    Note over UC: Pipeline finished 🌞
```

## What each phase does

### Phase 1 — `POST /build-dbt`

`etl_ecom` calls `HttpSemanticLayerAdapter.build_dbt()`, which sends an HTTP POST to the semantic layer service. The service spawns `dbt build` as a subprocess. dbt compiles each model into SQL, sends it to **Trino**, which resolves table locations through **Nessie** (Iceberg catalog) and reads raw Parquet files from **MinIO**. Transformed results are written back to MinIO as new Iceberg snapshots (silver → mart layers).

### Phase 2 — `POST /index`

`etl_ecom` calls `HttpSemanticLayerAdapter.index()`. The service first **recreates the Qdrant collection** (drops stale vectors), then runs two indexers in sequence:

- **`SemanticModelsIndexer`**: reads `semantic_models/*.yml`, builds a descriptive text per model (name + measures + dimensions), sends it to the **OpenAI embedding API**, and inserts the resulting vector into Qdrant with metadata `type=semantic_model`.
- **`MetricIndexer`**: reads `metrics/*.yml`, builds a text per metric (name + description + type + measure), embeds it, inserts into Qdrant with `type=metric`.

After indexing, the Qdrant collection holds vectors for every semantic model and metric — ready to serve similarity searches when the `/ask` endpoint receives a user question.
