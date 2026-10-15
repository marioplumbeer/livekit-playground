from livekit.agents import Agent, RunContext, function_tool
from livekit.agents.llm import DuplexSession

from livekit_playground.core.agents.technical_support.model import UserDataContact


class BasicAgent(Agent):
    def __init__(self, instructions: str):
        super().__init__(instructions=instructions)

    @property
    def duplex_session_or_none(self) -> DuplexSession | None:
        try:
            return self.duplex_session
        except RuntimeError:
            return None

    async def on_enter(self):
        handle = self.session.generate_reply(instructions="Greet the user and ask how you can help them.")

        await handle
        if handle.exception() is not None:
            print("the model declined to greet the user")

    @function_tool
    async def create_new_ticket(self, ctx: RunContext, ticket_urgency: str, ticket_timeline: str) -> str:
        """
        Create a new ticket for the user.
        Use once the user has provided the ticket details.

        Ask for one argument at a time.
        Do not ask for all four at once.

        Args:
            ticket_urgency (str): The urgency of the ticket, such as critical or medium.
            ticket_timeline (str): When did the issue start.
        """
        if ctx.session.userdata.ticket_number is not None:
            return "A ticket has already been created. Ask if they wish to repeat the ticket number."

        ctx.session.userdata.ticket_number = "123456"
        await self.update_tools([self.wait_for_user, self.end_call])

        context = f"""
            ## Ticket Details
            - User Request: {ctx.session.userdata.help_needed}
            - Ticket Number: {ctx.session.userdata.ticket_number}
            - Ticket Urgency: {ticket_urgency}
            - Ticket Timeline: {ticket_timeline}

            ### Next Steps
            1. A dispatcher will assign the ticket to an appropriate support squad.
            2. A technician will call the user back to confirm their contact details.
            3. The user and the technician will discuss a resolution.
        """

        if self.duplex_session_or_none:
            self.duplex_session.append_instructions(context)
        else:
            await self.update_instructions(f"""
                {self.instructions}

                {context}
            """)
        return f"""
            The ticket has been created with number {ctx.session.userdata.ticket_number}.
            Ask if they wish to repeat the ticket number or know what the next steps are.
        """

    @function_tool
    async def collect_contact_information(self, ctx: RunContext, first_name: str, last_name: str, company: str) -> str:
        """
        Collect the contact details from the user.
        Use once the user has provided their first name, last name and company.

        Collect their first name, then their last name, then their company. In that order.

        Args:
            first_name (str): The first name of the contact.
            last_name (str): The last name of the contact.
            company (str): The company of the contact.
        """
        if ctx.session.userdata.contact_details:
            return "Contact details have already been collected. Continue naturally with the next step."

        ctx.session.userdata.contact_details = UserDataContact(
            first_name=first_name, last_name=last_name, company=company
        )

        return "The contact details have been collected. Now you can create a new ticket for the user."

    @function_tool
    async def collect_user_request(self, ctx: RunContext, user_request_summary: str) -> str:
        """
        Collect the user's request once you understand what they need.
        Use for reported issues, requests to speak with a person, or any other need.

        Args:
            user_request_summary: A concise summary of what the user is asking for or reporting, including relevant
            details they mentioned.
        """
        if ctx.session.userdata.help_needed is not None:
            return "The user request has already bee collected. Continue naturally with the next step."
        ctx.session.userdata.help_needed = user_request_summary

        return """
            The user request is clear. Now you need to identify the user before logging their request.
            Go ahead and collect their contact details.
        """

    @function_tool
    async def wait_for_user(self) -> None:
        """
        Call this when the latest audio does not need a spoken response, such as silence,
        background noise, hold music, TV audio, side conversation, non-English speech
        or speech not addressed to the assistant. This tool helps end the turn without
        a spoken reply.
        """
        return None

    @function_tool
    async def end_call(self, ctx: RunContext) -> None:
        """
        End the call.
        Use when the user wants to end the call or hang up.
        """
        return "Promise a call back and say farewell."
