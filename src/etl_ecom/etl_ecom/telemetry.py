import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

_OTLP_ENDPOINT = os.getenv(
    "OTEL_EXPORTER_OTLP_ENDPOINT",
    "otel-collector.observability.svc.cluster.local:4318",
)

_provider_initialized = False


def setup_tracing(service_name: str) -> trace.Tracer:
    """Initialize the OTel TracerProvider once per process and return a tracer.

    Safe to call multiple times — subsequent calls return a tracer from the
    already-configured global provider without re-initializing.
    """
    global _provider_initialized
    if not _provider_initialized:
        resource = Resource.create({SERVICE_NAME: service_name})
        provider = TracerProvider(resource=resource)
        provider.add_span_processor(
            SimpleSpanProcessor(
                OTLPSpanExporter(endpoint=_OTLP_ENDPOINT, insecure=True)
            )
        )
        trace.set_tracer_provider(provider)
        _provider_initialized = True
    return trace.get_tracer(service_name)
