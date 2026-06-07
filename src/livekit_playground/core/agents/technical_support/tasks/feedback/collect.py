from livekit.agents import AgentTask, ChatContext, RunContext, function_tool

from livekit_playground.core.agents.technical_support.tasks.feedback.model import FeedbackTaskResult


class FeedbackCollectTask(AgentTask[FeedbackTaskResult]):
    def __init__(self, chat_ctx: ChatContext = None) -> None:
        super().__init__(
            instructions="Collect feedback from the customer.",
            chat_ctx=chat_ctx,
        )

    async def on_enter(self):
        await self.session.generate_reply(instructions="Ask the customer to provide comments about the support.")

    @function_tool
    async def collect(self, ctx: RunContext, comments: str) -> None:
        """
        Call when the customer has provided their feedback.

        Args:
            comments (str): The comments provided by the customer.
        """
        result = FeedbackTaskResult(comments=comments)
        self.complete(result=result)
