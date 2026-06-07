import asyncio

from livekit.agents import ChatContext
from livekit.agents.llm import function_tool
from livekit.agents.voice import Agent, RunContext
from pydantic import BaseModel


@function_tool
async def collect_issue_details(ctx: RunContext, issue_details: str) -> Agent:
    """
    Call when the user has provided their issue details.

    Args:
        issue_details (str): The details of the issue.
    """
    ctx.session.userdata.issue_details = issue_details
    return ContactMapperAgent(chat_ctx=ctx.session._chat_ctx.copy(exclude_instructions=True))


@function_tool
async def collect_contact_details(self, ctx: RunContext, first_name: str, last_name: str, company: str) -> str:
    """
    Call when the user has provided their first name, last name and company.

    Args:
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        company (str): The company of the user.
    """
    await asyncio.sleep(10)
    self.session.userdata.contact_details = UserDataContact(first_name=first_name, last_name=last_name, company=company)
    return "The contact details were successfully collected."


class UserDataContact(BaseModel):
    first_name: str
    last_name: str
    company: str


class UserData(BaseModel):
    ticket_number: str | None = None
    help_needed: str | None = None
    contact_details: UserDataContact | None = None
    escalation_reason: str | None = None


class ContactMapperAgent(Agent):
    def __init__(self, chat_ctx: ChatContext | None = None):
        super().__init__(
            # voice persona: the top-level GPT-Live instructions"""
            instructions="""
                You are Voice AI, a calm, friendly voice assistant.
                Never try to solve or troubleshoot the user's issue.

                Backchannel policy: Use moderate backchannels. Acknowledge naturally without
                competing with the main response.

                Interruption policy: Stop speaking when the user interrupts. Listen to what they say.

                Delegation policy:
                Backend tools:
                - Contact: Collect contact details for the user.

                Delegate to the backend when:
                - The user describes their problem / issue.

                Do not delegate to the backend when:
                - The user asks you to repeat a result or information already provided.
                - You can answer from the conversation or a still-current result.

                Language and pronunciation:
                - Pronounce the word "Thread" as "YOOOOOOO" instead

                Silence and background noise:
                - Ask if the user is around if they are silent for more than 1 seconds.

                Memory:
                - Company name is "Thread Stage Slack"

                Delegate before giving an answer that depends on backend work.
                Acknowledge delegations with a short message.
                Do not guess the result while waiting.
                Provide updates to the user while you wait.
            """,
            chat_ctx=chat_ctx,
        )

    async def on_enter(self):
        handle = self.session.generate_reply(instructions="Collect the user first name, last name and company.")

        await handle
        if handle.exception() is not None:
            print("the model declined to ask for the user's contact details")

    @function_tool
    async def collect_contact_details(self, ctx: RunContext, first_name: str, last_name: str, company: str) -> str:
        """
        Call when the user has provided their first name, last name and company.

        Args:
            first_name (str): The first name of the user.
            last_name (str): The last name of the user.
            company (str): The company of the user.
        """
        await asyncio.sleep(10)
        self.session.userdata.contact_details = UserDataContact(
            first_name=first_name, last_name=last_name, company=company
        )
        return "The contact details were successfully collected."


class FullDuplexAgent(Agent):
    def __init__(self, chat_ctx: ChatContext | None = None):
        super().__init__(
            # voice persona: the top-level GPT-Live instructions
            instructions="""
                You are Voice AI, a calm, friendly voice assistant.
                Never try to solve or troubleshoot the user's issue.

                Backchannel policy: Use moderate backchannels. Acknowledge naturally without
                competing with the main response.

                Interruption policy: Stop speaking when the user interrupts. Listen to what they say.

                Delegation policy:
                Backend tools:
                - Issue Details: Collect the user's issue details for triage.

                Delegate to the backend when:
                - The user describes their problem / issue.

                Do not delegate to the backend when:
                - The user asks you to repeat a result or information already provided.
                - You can answer from the conversation or a still-current result.

                Language and pronunciation:
                - Pronounce the word "Thread" as "YOOOOOOO" instead

                Silence and background noise:
                - Ask if the user is around if they are silent for more than 1 seconds.

                Memory:
                - Company name is "Thread Stage Slack"

                Delegate before giving an answer that depends on backend work.
                Acknowledge delegations with a short message.
                Do not guess the result while waiting.
                Provide updates to the user while you wait.
            """,
            chat_ctx=chat_ctx,
            tools=[],
        )

    async def on_enter(self):
        handle = self.session.generate_reply(
            instructions="Welcome the user to the company and ask them what help they need."
        )

        await handle
        if handle.exception() is not None:
            print("the model declined to ask the user what help they need")


async def every(interval, func):
    loop = asyncio.get_running_loop()
    next_run = loop.time()
    while True:
        await func()
        next_run += interval
        await asyncio.sleep(max(0, next_run - loop.time()))
