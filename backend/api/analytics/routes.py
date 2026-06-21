from fastapi import APIRouter, Depends
from typing import Annotated, Dict

from api.auth.routes import get_current_user
from services.analytics.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/", response_model=Dict)
async def get_analytics(
    current_user_id: Annotated[str, Depends(get_current_user)] = None
):
    """Get comprehensive analytics for the user"""
    analytics_service = AnalyticsService()
    analytics = await analytics_service.get_user_analytics(current_user_id)
    return analytics


@router.get("/dashboard", response_model=Dict)
async def get_dashboard(
    current_user_id: Annotated[str, Depends(get_current_user)] = None
):
    """Get dashboard data for the user"""
    analytics_service = AnalyticsService()
    dashboard_data = await analytics_service.get_dashboard_data(current_user_id)
    return dashboard_data
