from livekit.agents import AgentTask, ChatContext, function_tool

from livekit_playground.core.agents.technical_support.tasks.ticket.model import TicketStatus, TicketTaskResult

TicketAddNoteTaskResult = TicketTaskResult


class TicketAddNoteTask(AgentTask[TicketAddNoteTaskResult]):
    def __init__(self, ticket_number: str, chat_ctx: ChatContext = None) -> None:
        super().__init__(
            instructions="""
            Your role is to add the note the user wants to a ticket.
            """,
            chat_ctx=chat_ctx,
        )
        self._ticket_number = ticket_number

    async def on_enter(self):
        await self.session.generate_reply(instructions="Ask the note the user wants to add to the ticket.")

    @function_tool
    async def add_note(self, ticket_note: str) -> None:
        """
        Call when the customer has provided the note to add to the ticket.
        """
        result = TicketAddNoteTaskResult(
            summary="Laptop not turning on",
            urgency="critical",
            timeline="last week",
            number=self._ticket_number,
            notes=[ticket_note],
            status=TicketStatus.OPEN,
        )
        self.complete(result=result)
