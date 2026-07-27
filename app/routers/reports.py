"""Admin reports over archived data. Filters combine with AND."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies.auth import require_admin
from app.dependencies.report import ReportServiceDep
from app.schemas.report import Report, ReportFilters

router = APIRouter(
    prefix="/admin/reports", tags=["reports"], dependencies=[Depends(require_admin)]
)


@router.get("", response_model=Report)
async def get_report(
    filters: Annotated[ReportFilters, Depends()], service: ReportServiceDep
):
    """Totals and per-hotel / per-worker breakdowns over the filtered listings."""
    return await service.build(filters)
