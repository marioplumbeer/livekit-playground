from livekit.agents import Agent, RunContext, function_tool
from livekit.agents.beta.workflows import TaskGroup

from livekit_playground.core.agents.technical_support.model import UserData
from livekit_playground.core.agents.technical_support.tasks.contact.collect import CollectContactTask
from livekit_playground.core.agents.technical_support.tasks.feedback.collect import FeedbackCollectTask
from livekit_playground.core.agents.technical_support.tasks.ticket.create import TicketCreateTask


class SupervisorAgent(Agent):
    def __init__(self, instructions: str):
        super().__init__(instructions=instructions)

    async def on_enter(self):
        await self.session.generate_reply(
            instructions="Greet the user and ask how you can assist them.",
        )

    @property
    def userdata(self) -> UserData:
        return self.session.userdata

    @function_tool(on_duplicate="reject", duplicate_scope="name")
    async def record_user_request(self, ctx: RunContext, request_summary: str) -> str:
        """
        Call immediately when the user provides a request, statement or issue.
        Record the user's request once you understand what they need.
        Use for reported issues, requests to speak with a person, or any other need.

        Args:
            request_summary: A concise summary of what the user is asking for or reporting, including
            relevant details they mentioned.
        """
        ctx.session.userdata.help_needed = request_summary
        # TODO: figure out how to prevent the user from going back to previous step
        task_group = TaskGroup(chat_ctx=self.chat_ctx)
        task_group.add(
            lambda: CollectContactTask(chat_ctx=self.chat_ctx),
            id="collect_contact_task",
            description="Collects the contact information from the user.",
        )
        task_group.add(lambda: TicketCreateTask(), id="create_ticket_task", description="Creates a new ticket.")

        try:
            result = await task_group
            self.userdata.ticket_number = result.task_results["create_ticket_task"].result.number
            self.instructions += f"\n\nTicket Number: <spell>{self.userdata.ticket_number}</spell>."
            return FeedbackCollectTask(chat_ctx=self.chat_ctx)
        except Exception as e:
            return f"An error occurred while creating the ticket: {e}"
