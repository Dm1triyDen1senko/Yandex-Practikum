from typing import Dict, List

from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.crud.charity_project import CRUDCharityProject
from app.services.google_api import (set_user_permissions, spreadsheets_create,
                                     spreadsheets_update_value)

from app.models import CharityProject

router = APIRouter()


@router.get(
    '/',
    response_model=List[Dict],
    dependencies=[Depends(current_superuser)]
)
async def get_report(
    session: AsyncSession = Depends(get_async_session),
    wrapper_services: Aiogoogle = Depends(get_service)
):
    """Только для суперюзеров!"""
    charity_project_crud = CRUDCharityProject(CharityProject)

    projects = await charity_project_crud.get_projects_by_completion_rate(
        session
    )

    spreadsheet_id = await spreadsheets_create(wrapper_services)

    await set_user_permissions(spreadsheet_id, wrapper_services)

    await spreadsheets_update_value(spreadsheet_id, projects, wrapper_services)

    return projects
