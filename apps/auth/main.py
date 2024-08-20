from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from api import api_router
from core.settings import settings
from db import postgres, redis
from rate_limiter import check_limit


@asynccontextmanager
async def lifespan(_: FastAPI):
    postgres.setup_postgres_connection()
    redis.setup_redis_connection()
    yield
    await redis.close_redis_connection()
    await postgres.close_postgres_connection()


app = FastAPI(
    title=settings.api.TITLE,
    docs_url=settings.api.DOCS_URL,
    openapi_url=settings.api.OPENAPI_URL,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    root_path="/auth",
)
app.include_router(api_router)


def configure_tracer() -> None:
    jaeger_exporter = JaegerExporter(agent_host_name=settings.jaeger.HOST, agent_port=settings.jaeger.PORT)
    trace.set_tracer_provider(TracerProvider(resource=Resource.create({SERVICE_NAME: "auth-service"})))
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))


if not settings.api.DEBUG:
    configure_tracer()
    FastAPIInstrumentor.instrument_app(app)


@app.middleware("http")
async def before_request(request: Request, call_next):
    if not settings.api.DEBUG:
        request_id = request.headers.get("X-Request-Id")
        user_id = request.headers.get("X-Forwarded-For")

        overage = await check_limit(user_id=user_id)
        if overage:
            return ORJSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS, content={"detail": "Too many requests"}
            )

        if not request_id:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "X-Request-Id is required"}
            )

        tracer: trace.Tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("auth-api") as span:
            span.set_attribute("http.request_id", request_id)

    response = await call_next(request)
    return response
