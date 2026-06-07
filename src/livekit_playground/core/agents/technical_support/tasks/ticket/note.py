from livekit.agents import AgentTask, ChatContext, function_tool

from livekit_playground.core.agents.technical_support.tasks.ticket.model import TicketStatus, TicketTaskResult

TicketNoteTaskResult = TicketTaskResult


class TicketNoteTask(AgentTask[TicketNoteTaskResult]):
    def __init__(self, ticket_number: str, chat_ctx: ChatContext = None) -> None:
        super().__init__(
            instructions="Adds a note to an existing ticket.",
            chat_ctx=chat_ctx,
        )
        self._ticket_number = ticket_number

    async def on_enter(self):
        await self.session.generate_reply()

    @function_tool
    async def add(self, note: str) -> None:
        """
        Call when the customer has provided their ticket note.

        Args:
            note (str): The ticket note provided by the customer.
        """
        result = TicketNoteTaskResult(
            details="Laptop not turning on", number=self._ticket_number, status=TicketStatus.OPEN, notes=[note]
        )
        self.complete(result=result)
