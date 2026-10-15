from livekit.agents import AgentTask, ChatContext, function_tool

from livekit_playground.core.agents.technical_support.tasks.contact.model import CollectContactTaskResult


class CollectContactTask(AgentTask[CollectContactTaskResult]):
    def __init__(self, chat_ctx: ChatContext = None) -> None:
        super().__init__(
            instructions="""
            Your role is to identify the user.
            You should collect their contact information, such as first name, last name and company.
            """,
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions="""
                Let the user know you need to identify them.
                Then, collect the user's first name, then last name, then company. In this order.
            """,
        )

    @function_tool
    async def collect_contact_information(self, first_name: str, last_name: str, company: str) -> None:
        """
        Collect the contact details from the user.
        Use once the user has provided their first name, last name and company.

        Collect their first name, then their last name, then their company. In that order.

        Args:
            first_name (str): The first name of the contact.
            last_name (str): The last name of the contact.
            company (str): The company of the contact.
        """
        self.complete(
            CollectContactTaskResult(first_name=first_name, last_name=last_name, company=company),
        )
