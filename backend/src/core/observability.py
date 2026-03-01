from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_fastapi_instrumentator import Instrumentator

from core.config import get_settings


def setup_observability(app: FastAPI) -> None:
    settings = get_settings()

    trace_provider = TracerProvider(
        resource=Resource.create({"service.name": settings.otel_service_name}),
    )
    span_exporter = OTLPSpanExporter(endpoint=settings.otlp_endpoint, insecure=True)
    trace_provider.add_span_processor(BatchSpanProcessor(span_exporter))
    trace.set_tracer_provider(trace_provider)

    FastAPIInstrumentor.instrument_app(app, tracer_provider=trace_provider)
    Instrumentator().instrument(app).expose(app, include_in_schema=False)
