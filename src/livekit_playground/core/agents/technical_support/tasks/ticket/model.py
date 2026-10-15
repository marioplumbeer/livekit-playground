from enum import StrEnum

from pydantic import BaseModel


class TicketStatus(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"


class TicketTaskResult(BaseModel):
    summary: str
    urgency: str
    timeline: str
    number: str
    notes: list[str]
    status: TicketStatus
