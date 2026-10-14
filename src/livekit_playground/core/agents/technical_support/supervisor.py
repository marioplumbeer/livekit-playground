from livekit.agents import Agent, RunContext, function_tool
from livekit.agents.beta.workflows import TaskGroup

from livekit_playground.core.agents.technical_support.model import UserData
from livekit_playground.core.agents.technical_support.tasks.contact.collect import CollectContactTask
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

    @function_tool
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
            await self.update_instructions(
                instructions=f"""
            {self.instructions}

            ## Ticket Details
            - User Request: {request_summary}
            - Ticket Number: <spell>{self.userdata.ticket_number}</spell>.
            - Ticket Urgency: {result.task_results["create_ticket_task"].result.details.urgency}
            - Ticket Impact: {result.task_results["create_ticket_task"].result.details.timeline}
            - Ticket Timeline: {result.task_results["create_ticket_task"].result.details.timeline}

            ### Next Steps
            1. A dispatcher will assign the ticket to an appropriate support squad.
            2. A technician will call the user back to confirm their contact details.
            3. The user and the technician will discuss a resolution.
            """
            )

            await self.session.generate_reply(
                instructions="""
                Their request has been logged. Ask if they wish to repeat the
                ticket number or know what the next steps are.
            """
            )
            return ""
        except Exception as e:
            return f"An error occurred while creating the ticket: {e}"

    @function_tool
    async def end_call(self, ctx: RunContext) -> None:
        """
        End the call.
        Use when the user wants to end the call or hang up.
        """
        return "Promise a call back and say farewell."
