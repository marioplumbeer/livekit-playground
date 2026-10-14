from livekit.agents import AgentTask, ChatContext, function_tool

from livekit_playground.core.agents.technical_support.tasks.contact.model import CollectContactTaskResult


class CollectContactTask(AgentTask[CollectContactTaskResult]):
    def __init__(self, chat_ctx: ChatContext = None) -> None:
        super().__init__(
            instructions="""
            In order to help the user, we need collect their contact information.
            Collect the contact information from the user.
            """,
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions="""
                Now you need to identify the user before proceeding to the next step.
                Go ahead and collect their first name, last name and company. In this order.
            """,
        )

    @function_tool
    async def collect_contact_information(self, first_name: str, last_name: str, company: str) -> None:
        """
        Use once the user has provided their first name, last name and company.

        Args:
            first_name (str): The first name of the contact.
            last_name (str): The last name of the contact.
            company (str): The company of the contact.
        """
        self.complete(
            CollectContactTaskResult(first_name=first_name, last_name=last_name, company=company),
        )
