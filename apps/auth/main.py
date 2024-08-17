from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from api import api_router
from core.settings import settings
from db import postgres, redis


@asynccontextmanager
async def lifespan(_: FastAPI):
    postgres.setup_postgres_connection()
    redis.setup_redis_connection()
    yield
    await redis.close_redis_connection()
    await postgres.close_postgres_connection()


def configure_tracer() -> None:
    jaeger_exporter = JaegerExporter(agent_host_name=settings.jaeger.HOST, agent_port=settings.jaeger.PORT)
    trace.set_tracer_provider(TracerProvider(resource=Resource.create({SERVICE_NAME: "auth-service"})))
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))
    # Чтобы видеть трейсы в консоли
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


configure_tracer()

app = FastAPI(
    title=settings.api.TITLE,
    docs_url=settings.api.DOCS_URL,
    openapi_url=settings.api.OPENAPI_URL,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(api_router)

FastAPIInstrumentor.instrument_app(app)


@app.middleware('http')
async def before_request(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': 'X-Request-Id is required'})
    return response
