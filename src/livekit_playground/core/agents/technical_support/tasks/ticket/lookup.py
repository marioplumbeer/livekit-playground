from livekit.agents import AgentTask, ChatContext, function_tool

from livekit_playground.core.agents.technical_support.tasks.ticket.model import TicketStatus, TicketTaskResult

TicketLookupTaskResult = TicketTaskResult


class TicketLookupTask(AgentTask[TicketLookupTaskResult]):
    def __init__(self, chat_ctx: ChatContext = None) -> None:
        super().__init__(
            instructions="""
            Your role is to look up an existing ticket.
            """,
            chat_ctx=chat_ctx,
        )

    async def on_enter(self):
        await self.session.generate_reply(
            instructions="Ask for the ticket summary or number.",
        )

    @function_tool
    async def ticket_details_collected(self, summary: str | None, number: str | None) -> None:
        """
        Call when the customer has provided their ticket summary or number
        """
        self.complete(
            result=TicketLookupTaskResult(
                summary=summary or "laptop is broken",
                urgency="critical",
                timeline="started last week",
                number=number or "123456",
                notes=[
                    "tech on site",
                    "cable repaired",
                    "pending order update",
                ],
                status=TicketStatus.OPEN,
            )
        )
