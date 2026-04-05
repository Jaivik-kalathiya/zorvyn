from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.rate_limit import register_rate_limiter
from app.core.report_scheduler import start_report_scheduler, stop_report_scheduler
from app.db.init_db import create_tables

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_tables()
    scheduler = start_report_scheduler()
    yield
    stop_report_scheduler(scheduler)


app = FastAPI(title=settings.APP_NAME, debug=settings.APP_DEBUG, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
register_rate_limiter(app)


app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
