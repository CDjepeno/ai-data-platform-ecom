import os
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from routes.ask import router as ask_router
from routes.build_dbt import router as build_dbt_router
from routes.indexing import router as indexing_router
from routes.health import router as health_router
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


def _setup_tracing() -> None:
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector.observability.svc.cluster.local:4318")
    service_name = os.getenv("OTEL_SERVICE_NAME", "semantic_layer")
    provider = TracerProvider(resource=Resource({SERVICE_NAME: service_name}))
    provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces"))
    )
    trace.set_tracer_provider(provider)


_setup_tracing()

app = FastAPI()

FastAPIInstrumentor().instrument_app(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)

app.include_router(ask_router)
app.include_router(build_dbt_router)
app.include_router(indexing_router)
app.include_router(health_router)
