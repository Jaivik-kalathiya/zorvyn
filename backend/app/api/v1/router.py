from fastapi import APIRouter

from app.api.v1.endpoints import auth, dashboard, records, reports, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(records.router, prefix="/records", tags=["records"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
