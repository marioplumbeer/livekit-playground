from enum import StrEnum

from pydantic import BaseModel


class TicketStatus(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"


class TicketDetails(BaseModel):
    description: str
    urgency: str
    timeline: str
    impact: str


class TicketTaskResult(BaseModel):
    details: TicketDetails
    notes: list[str]
    number: str
    status: TicketStatus

    def __str__(self) -> str:
        items = [
            f"Ticket Number: {self.number}",
            f"Ticket Status: {self.status}",
            f"Ticket Description: {self.details.description}",
            f"Ticket Urgency: {self.details.urgency}",
            f"Ticket Timeline: {self.details.timeline}",
            f"Ticket Impact: {self.details.impact}",
        ]
        if self.notes:
            notes_as_string = "\n- ".join(self.notes)
            items.append(f"Ticket Notes: \n- {notes_as_string}")
        return "\n\n".join(items)
