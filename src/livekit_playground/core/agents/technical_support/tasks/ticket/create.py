import uuid

from livekit.agents import AgentTask, ChatContext, RunContext, function_tool

from livekit_playground.core.agents.technical_support.tasks.ticket.model import (
    TicketDetails,
    TicketStatus,
    TicketTaskResult,
)

TicketCreateTaskResult = TicketTaskResult


class TicketCreateTask(AgentTask[TicketCreateTaskResult]):
    def __init__(self, chat_ctx: ChatContext = None) -> None:
        super().__init__(
            instructions="Create a new ticket.",
            chat_ctx=chat_ctx,
        )
        self._ticket = None

    async def on_enter(self) -> None:
        await self.session.generate_reply()

    @function_tool
    async def create(self, ctx: RunContext, details: TicketDetails) -> None:
        """
        Call when the customer has provided their ticket details.

        Args:
            details (TicketDetails): The ticket details provided by the customer.
        """
        self._ticket = TicketCreateTaskResult(
            details=details, number=str(uuid.uuid4()), status=TicketStatus.OPEN, notes=[]
        )
        return f"The ticket has been created with number <spell>{self._ticket.number}</spell>."
