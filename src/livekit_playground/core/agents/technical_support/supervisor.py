from livekit.agents import Agent, RunContext, function_tool

from livekit_playground.core.agents.technical_support.model import UserData
from livekit_playground.core.agents.technical_support.tasks.contact.collect import CollectContactTask
from livekit_playground.core.agents.technical_support.tasks.ticket.add_note import TicketAddNoteTask
from livekit_playground.core.agents.technical_support.tasks.ticket.create import TicketCreateTask
from livekit_playground.core.agents.technical_support.tasks.ticket.lookup import TicketLookupTask


class SupervisorAgent(Agent):
    def __init__(self, instructions: str):
        super().__init__(
            instructions="""
                You are a helpful Voice Attendant for the IT-Support company.

                Route their request:
                - For issues or problems, call log_issue.
                - For questions about existing tickets, call lookup_ticket.
                - For adding notes to tickets, call add_note_to_ticket.
                - For call backs, call call_back.
                - For escalation requests, call escalate.
                - For resetting passwords, call reset_password.
                - For all other enquires, answer directly from context. If the information is not available, say so.

                After a tool returns, summarize the outcome and ask whether the caller needs anything else.
            """
        )

    async def on_enter(self):
        await self.session.generate_reply(
            instructions="Greet the user and ask how you can help them.",
        )

    @property
    def userdata(self) -> UserData:
        return self.session.userdata

    async def auth_contact(self):
        if self.userdata.contact_details is None:
            self.userdata.contact_details = await CollectContactTask(
                chat_ctx=self.chat_ctx.copy(exclude_instructions=True),
            )

            self.update_instructions(
                instructions=f"""
            {self.instructions}

            # Context
            ## Contact
            - First Name: {self.userdata.contact_details.first_name}
            - Last Name: {self.userdata.contact_details.last_name}
            - Company: {self.userdata.contact_details.company}
            """
            )

    @function_tool
    async def log_issue(self) -> str:
        """
        Use when the user reports an issue or problem of any sorts.
        """

        await self.auth_contact()
        ticket = await TicketCreateTask(
            chat_ctx=self.chat_ctx.copy(exclude_instructions=True),
        )
        return f"Logged issue with number <spell>{ticket.number}</spell>"

    @function_tool
    async def add_note_to_ticket(self) -> str:
        """
        Use when the user wants to add a note to a ticket.
        """

        await self.auth_contact()
        ticket = await TicketLookupTask(
            chat_ctx=self.chat_ctx.copy(exclude_instructions=True),
        )
        await TicketAddNoteTask(
            chat_ctx=self.chat_ctx.copy(exclude_instructions=True),
            ticket_number=ticket.number,
        )
        return f"The note has been added to the ticket with number <spell>{ticket.number}</spell>"

    @function_tool
    async def lookup_ticket(self) -> str:
        """
        Use when the user wants to check the status of a ticket.
        """

        await self.auth_contact()
        ticket = await TicketLookupTask(
            chat_ctx=self.chat_ctx.copy(exclude_instructions=True),
        )
        return f"Ticket <spell>{ticket.number}</spell> is {ticket.status}. The latest update is {ticket.notes[-1]}"

    @function_tool
    async def call_back(self) -> str:
        """
        Use when the user is returning a call.
        """

        await self.auth_contact()
        latest_update = "a technician is on site fixing your issue."
        ticket_status = "in review"
        issue_number = "123456"
        return f"Ticket <spell>{issue_number}</spell> is {ticket_status}: {latest_update}"

    @function_tool
    async def escalate(self, escalation_reason: str) -> str:
        """
        Use when the user wants to talk to someone, such as a human, technician, person directly.
        """

        await self.auth_contact()
        escalation_number = "123456"
        return f"Escalated request with number <spell>{escalation_number}</spell> due to {escalation_reason}"

    @function_tool
    async def reset_password(self) -> str:
        """
        Use when the user wants to reset their password.
        """
        await self.auth_contact()
        return "The password has been reset."

    @function_tool
    async def end_call(self, ctx: RunContext) -> None:
        """
        Use when the user wants to end the call or hang up.
        """
        return "Promise a call back and say farewell."
