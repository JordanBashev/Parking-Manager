"""Providers for the report layer."""

from typing import Annotated

from fastapi import Depends

from app.dependencies.db import SessionDep
from app.repositories.report import ReportRepository
from app.services.report import ReportService


def get_report_repository(session: SessionDep) -> ReportRepository:
    return ReportRepository(session)


ReportRepositoryDep = Annotated[ReportRepository, Depends(get_report_repository)]


def get_report_service(repository: ReportRepositoryDep) -> ReportService:
    return ReportService(repository)


ReportServiceDep = Annotated[ReportService, Depends(get_report_service)]
