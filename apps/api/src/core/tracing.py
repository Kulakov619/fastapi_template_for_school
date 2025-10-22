from core.config import settings
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                            ConsoleSpanExporter)
from opentelemetry.semconv.resource import ResourceAttributes

# def configure_tracer() -> None:
#     resource = Resource(
#         attributes={ResourceAttributes.SERVICE_NAME: settings.service_name},
#     )
#     tracer_provider = TracerProvider(resource=resource)
#
#     trace.set_tracer_provider(tracer_provider)
#     trace.get_tracer_provider().add_span_processor(
#         BatchSpanProcessor(
#             JaegerExporter(
#                 agent_host_name=settings.jaeger_host,
#                 agent_port=settings.jaeger_port,
#             ),
#         ),
#     )
#     # # Чтобы видеть трейсы в консоли
#     # if settings.dev_enviroment:
#     #     trace.get_tracer_provider().add_span_processor(
#     #         BatchSpanProcessor(ConsoleSpanExporter()),
#     #     )
#
#
# def init_tracing(app: FastAPI) -> None:
#     configure_tracer()
#     FastAPIInstrumentor.instrument_app(app)
