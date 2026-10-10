import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)

from app.config import get_settings
from app.routes.api import router as api_router
from app.services.reliability import reliability_service

# Structured JSON Logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s", "level":"%(levelname)s", "service":"cloudops", "message":"%(message)s"}',
)
logger = logging.getLogger("cloudops")

settings = get_settings()

# --- Prometheus Metrics (RED Method) ---
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP request count",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.app_name} v{settings.app_version} in [{settings.app_env}] mode")
    yield
    logger.info(f"Shutting down {settings.app_name}")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url=None,
)


@app.middleware("http")
async def metrics_and_logging_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    endpoint = request.url.path

    # Avoid recursing on Prometheus scrape calls
    if endpoint == "/metrics":
        return await call_next(request)

    await reliability_service.apply_simulated_latency()

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception as exc:
        logger.error(f"Unhandled exception during {request.method} {endpoint}: {exc}")
        raise
    finally:
        latency = time.perf_counter() - start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status_code=status_code,
        ).inc()
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=endpoint,
        ).observe(latency)
        logger.info(
            f"method={request.method} path={endpoint} status={status_code} latency={latency:.4f}s"
        )


@app.get("/metrics", tags=["Observability"])
async def get_metrics():
    """Prometheus telemetry scrape endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


app.include_router(api_router)