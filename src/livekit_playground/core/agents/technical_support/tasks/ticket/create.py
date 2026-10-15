from livekit.agents import AgentTask, ChatContext, RunContext, function_tool

from livekit_playground.core.agents.technical_support.tasks.ticket.model import (
    TicketStatus,
    TicketTaskResult,
)

TicketCreateTaskResult = TicketTaskResult


class TicketCreateTask(AgentTask[TicketCreateTaskResult]):
    def __init__(self, chat_ctx: ChatContext = None) -> None:
        super().__init__(
            instructions=""""
            Your role is to create a new ticket for the user issue.
            """,
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(instructions="Continue the conversation naturally and create a new ticket.")

    @function_tool
    async def create_new_ticket(self, ctx: RunContext, ticket_urgency: str, ticket_timeline: str) -> None:
        """
        Create a new ticket for the user.
        Use once the user has provided the ticket details.

        Ask for one argument at a time.
        Do not ask for all four at once.

        Args:
            ticket_urgency (str): The urgency of the ticket, such as critical or medium.
            ticket_timeline (str): When did the issue start.
        """
        self.complete(
            TicketCreateTaskResult(
                summary="something is broken with laptop",
                urgency=ticket_urgency,
                timeline=ticket_timeline,
                number="123456",
                status=TicketStatus.OPEN,
                notes=[],
            )
        )
