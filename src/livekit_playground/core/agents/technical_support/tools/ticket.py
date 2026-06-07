from livekit.agents.llm import function_tool
from livekit.agents.voice import RunContext

from livekit_playground.core.agents.technical_support.tasks.ticket.create import TicketCreateTaskResult
from livekit_playground.core.agents.technical_support.tasks.ticket.lookup import TicketLookupTaskResult
from livekit_playground.core.agents.technical_support.tasks.ticket.model import TicketStatus
from livekit_playground.core.agents.technical_support.tasks.ticket.note import TicketNoteTaskResult


@function_tool
async def create_ticket(ctx: RunContext, issue_details: str) -> str:
    """
    Call when the customer has provided their issue details.

    Args:
        issue_details (str): The issue details provided by the customer.
    """
    result = TicketCreateTaskResult(
        details=issue_details,
        number="1",
        status=TicketStatus.OPEN,
        notes=[],
    )
    return str(result)


@function_tool
async def lookup_ticket(ctx: RunContext, ticket_summary: str | None = None, ticket_number: str | None = None) -> str:
    """
    Call when the customer has provided their ticket summary or number.

    Args:
        ticket_summary (str): The ticket summary provided by the customer.
        ticket_number (str): The ticket number provided by the customer.
    """
    result = TicketLookupTaskResult(
        details="Laptop not turning on" or ticket_summary,
        number=ticket_number or "1",
        status=TicketStatus.OPEN,
        notes=[],
    )
    return str(result)


@function_tool
async def add_note_to_ticket(ctx: RunContext, ticket_number: str, ticket_note: str) -> str:
    """
    Call when the customer has provided their ticket number and note.

    Args:
        ticket_number (str): The ticket number provided by the customer.
        ticket_note (str): The ticket note provided by the customer.
    """
    result = TicketNoteTaskResult(
        details="Laptop not turning on",
        number=ticket_number,
        status=TicketStatus.OPEN,
        notes=[ticket_note],
    )
    return str(result)
