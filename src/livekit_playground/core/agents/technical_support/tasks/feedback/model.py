from pydantic import BaseModel


class FeedbackTaskResult(BaseModel):
    comments: str

    def __str__(self) -> str:
        items = [
            f"Comments: {self.comments}",
        ]
        return "\n\n".join(items)
