from typing import Any, Dict, Optional
from database.repository import InvoiceRepository

class AuditService:
    def __init__(self, repository: Optional[InvoiceRepository] = None):
        self.repository = repository or InvoiceRepository()

    def record_event(
        self,
        run_id: str,
        event_type: str,
        actor: str = "SYSTEM",
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        return self.repository.log_audit_event(
            run_id=run_id,
            event_type=event_type,
            actor=actor,
            details=details or {}
        )

    def get_events_for_run(self, run_id: str):
        return self.repository.get_audit_events(run_id)
