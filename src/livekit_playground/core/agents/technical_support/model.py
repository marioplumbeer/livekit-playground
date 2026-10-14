from pydantic import BaseModel


class UserDataContact(BaseModel):
    first_name: str
    last_name: str
    company: str


class UserData(BaseModel):
    ticket_number: str | None = None
    help_needed: str | None = None
    contact_details: UserDataContact | None = None
    escalation_reason: str | None = None
