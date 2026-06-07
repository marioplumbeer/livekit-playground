from pydantic import BaseModel


class CollectContactTaskResult(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    company: str | None = None

    def __str__(self) -> str:
        items = [
            f"Contact First Name: {self.first_name}",
            f"Contact Last Name: {self.last_name}",
            f"Contact Company: {self.company}",
        ]
        return "\n\n".join(items)
