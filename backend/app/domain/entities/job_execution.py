"""
Job Execution Domain Entity
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid


@dataclass
class JobExecution:
    """
    Entidade de domínio para execução de jobs.
    Rastreia o histórico de execuções de jobs agendados.
    """
    job_name: str
    status: str  # 'pending', 'running', 'completed', 'failed', 'cancelled'
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    progress: float = 0.0  # 0.0 a 100.0
    total_editais: int = 0
    processed_editais: int = 0
    failed_editais: int = 0
    errors: List[Dict[str, Any]] = field(default_factory=list)
    result_summary: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(cls, job_name: str) -> "JobExecution":
        """Factory method para criar nova execução de job"""
        return cls(
            job_name=job_name,
            status="pending"
        )

    def start(self) -> None:
        """Marca o job como iniciado"""
        self.status = "running"
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def update_progress(self, processed: int, total: int) -> None:
        """Atualiza o progresso do job"""
        self.processed_editais = processed
        self.total_editais = total
        self.progress = (processed / total * 100) if total > 0 else 0
        self.updated_at = datetime.utcnow()

    def add_error(self, edital_url: str, error_message: str, retry_count: int = 0) -> None:
        """Adiciona um erro ao histórico"""
        self.errors.append({
            "edital_url": edital_url,
            "error": error_message,
            "retry_count": retry_count,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.failed_editais += 1
        self.updated_at = datetime.utcnow()

    def complete(self, summary: Optional[Dict[str, Any]] = None) -> None:
        """Marca o job como completado"""
        self.status = "completed"
        self.finished_at = datetime.utcnow()
        self.progress = 100.0
        self.result_summary = summary or {
            "total_editais": self.total_editais,
            "processed_editais": self.processed_editais,
            "failed_editais": self.failed_editais,
            "success_rate": (self.processed_editais / self.total_editais * 100) if self.total_editais > 0 else 0
        }
        self.updated_at = datetime.utcnow()

    def fail(self, error_message: str) -> None:
        """Marca o job como falho"""
        self.status = "failed"
        self.finished_at = datetime.utcnow()
        self.errors.append({
            "error": error_message,
            "timestamp": datetime.utcnow().isoformat(),
            "is_critical": True
        })
        self.updated_at = datetime.utcnow()

    def cancel(self) -> None:
        """Cancela o job"""
        self.status = "cancelled"
        self.finished_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def is_running(self) -> bool:
        """Verifica se o job está em execução"""
        return self.status == "running"

    def is_finished(self) -> bool:
        """Verifica se o job terminou (sucesso, falha ou cancelado)"""
        return self.status in ["completed", "failed", "cancelled"]

    def to_dict(self) -> Dict[str, Any]:
        """Converte a entidade para dicionário"""
        return {
            "id": self.id,
            "job_name": self.job_name,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "progress": self.progress,
            "total_editais": self.total_editais,
            "processed_editais": self.processed_editais,
            "failed_editais": self.failed_editais,
            "errors": self.errors,
            "result_summary": self.result_summary,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JobExecution":
        """Cria uma entidade a partir de um dicionário"""
        # Converter strings ISO para datetime
        if isinstance(data.get("started_at"), str):
            data["started_at"] = datetime.fromisoformat(data["started_at"])
        if isinstance(data.get("finished_at"), str):
            data["finished_at"] = datetime.fromisoformat(data["finished_at"])
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data.get("updated_at"), str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])

        return cls(**data)
