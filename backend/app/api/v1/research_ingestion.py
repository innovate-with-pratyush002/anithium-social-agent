from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_admin
from app.db.session import get_db_session
from app.schemas.research_ingestion import (
    ResearchIngestionRequest,
    ResearchIngestionResponse,
)
from app.services.research_ingestion import ingest_research

router = APIRouter(
    prefix="/research-ingestion",
    tags=["Research Ingestion"],
    dependencies=[Depends(require_admin)],
)


@router.post(
    "/run",
    response_model=ResearchIngestionResponse,
    status_code=status.HTTP_200_OK,
)
async def run_research_ingestion(
    payload: ResearchIngestionRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ResearchIngestionResponse:
    return await ingest_research(session, payload)
