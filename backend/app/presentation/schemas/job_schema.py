"""
Job Schemas - Modelos Pydantic para request/response de jobs
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


class JobExecutionResponse(BaseModel):
    """Schema de resposta para execução de job"""
    id: str
    job_name: str
    status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    progress: float
    total_editais: int
    processed_editais: int
    failed_editais: int
    errors: List[Dict[str, Any]]
    result_summary: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobExecuteResponse(BaseModel):
    """Schema de resposta para execução manual de job"""
    job_id: str
    message: str
    status_url: str


class JobListResponse(BaseModel):
    """Schema de resposta para lista de jobs"""
    jobs: List[JobExecutionResponse]
    total: int
