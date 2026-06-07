import os

from dotenv import load_dotenv
from livekit.agents import (
    AgentServer,
    AgentSession,
    JobContext,
    cli,
    inference,
)
from livekit.plugins import openai, silero

from livekit_playground.core.agents.technical_support.full_duplex import FullDuplexAgent, UserData
from livekit_playground.core.agents.technical_support.supervisor import SupervisorAgent

load_dotenv()


server = AgentServer()


@server.rtc_session()
async def entrypoint(ctx: JobContext):
    session, agent = None, None

    if os.getenv("DESIGN_PATTERN") == "supervisor":
        session = AgentSession(
            userdata=UserData(),
            vad=silero.VAD.load(),
            stt=inference.STT("deepgram/nova-3", language="multi"),
            llm=inference.LLM("openai/gpt-5.6-sol"),
            tts=inference.TTS("cartesia/sonic-3", voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"),
        )
        agent = SupervisorAgent(
            instructions="""
                GENERAL GUIDELINES:
                - Break grammar rules. Start sentences with "And," "But," or "So." Break grammar rules in the common
                ways that people break grammar rules. Use "like" often.
                - Pauses are fine; when you fill them, use "ya" <break time="300ms"/>, or "so yeah", or "anyway".
                - Whenever you say "um" then a <break>, pick up again with the natural option after the pause.
                - If confused or you think you misheard something: "Sorry, <break time="300ms"/> , I think I missed
                that, what did you say?"
                - Confirm your understanding of the user's request before proceeding.
                - Avoid sounding robotic or scripted. Use natural, conversational language.

                LEAN INTO THIS HARD:
                Everything below is essential. You are mid-conversation at a coffee shop, not presenting a keynote:
                - Filler words are good: "um," "so," "okay," "hm," "like," "ya so"

                NON-VERBAL SOUNDS:
                Use these sparingly, no more than one per turn:
                - After a self-deprecating remark from the user, lead with a brief [chuckles].
                - Before delivering bad news, [sighs] softly.
                - After a longer silence, start with [exhales] before continuing.

                PHRASE VARIATION:
                Don't open consecutive turns with the same word or acknowledgment. Rotate through different short
                phrases and avoid reusing the same one back to back.

                Examples:
                - Turn 1: "Yeah, um <break time="300ms"/> so, I can do that."
                - Turn 2: "Mhm, <break time="200ms"/> let me pull that up."
                - Turn 3: "Okay. One sec."
                - Turn 4: "Right, <break time="200ms"/> here's what I'm seeing."

                THINGS TO AVOID:
                - Do not output bullet points, numbered lists, or any structured formatting. Speak items naturally
                with pauses between them, and do not say "here's a list."
                - Do not use asterisks, hashtags, or markdown syntax. Do not wrap words in **bold** or *italics* —
                the engine will speak the asterisks.
                - Do not improvise details that were not provided.
                - Do not repeat the same information more than once unless asked.
                - Do not troubleshoot the user's issue.
            """
        )
    elif os.getenv("DESIGN_PATTERN") == "full_duplex":
        session = AgentSession[UserData](
            userdata=UserData(),
            llm=openai.realtime.GPTLiveModel(
                azure_deployment="gpt-live-1",
                base_url="https://ai-stage-03.openai.azure.com/",
                voice="marin",
                responses_options={
                    "model": "gpt-5.6-sol",
                    "instructions": """
                        You handle the work the voice model delegates. Use tools when
                        collecting information from the user,
                        and answer with a short result the voice model can read out.

                        When collecting information from the user, ask one question at a time.
                        Do not ask multiple questions at once.
                    """,
                    # "reasoning": {"effort": "none"},
                    # "text": {"verbosity": "low"},
                },
            ),
        )
        agent = FullDuplexAgent()

    if session and agent:
        await session.start(agent=agent, room=ctx.room)


def main():
    cli.run_app(server)


if __name__ == "__main__":
    main()
