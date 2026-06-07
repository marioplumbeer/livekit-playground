from livekit.agents import AgentTask, ChatContext, function_tool

from livekit_playground.core.agents.technical_support.tasks.ticket.model import TicketStatus, TicketTaskResult

TicketLookupTaskResult = TicketTaskResult


# TODO: split between collection vs. lookup
class TicketLookupTask(AgentTask[TicketLookupTaskResult]):
    def __init__(self, chat_ctx: ChatContext = None) -> None:
        super().__init__(
            instructions="Look up an existing ticket by summary or number.",
            chat_ctx=chat_ctx,
        )

    async def on_enter(self):
        await self.session.generate_reply()

    @function_tool
    async def find_by_summary(self, summary: str) -> None:
        """
        Call when the customer has provided their ticket summary.

        Args:
            summary (str): The ticket summary provided by the customer.
        """
        result = TicketLookupTaskResult(details=summary, number="1", status=TicketStatus.OPEN, notes=[])
        self.complete(result=result)

    @function_tool
    async def find_by_number(self, number: str) -> None:
        """
        Call when the customer has provided their ticket number.

        Args:
            number (str): The ticket number provided by the customer.
        """
        result = TicketLookupTaskResult(
            details="Laptop not turning on", number=number, status=TicketStatus.OPEN, notes=[]
        )
        self.complete(result=result)
