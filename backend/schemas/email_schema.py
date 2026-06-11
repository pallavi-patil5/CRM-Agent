from pydantic import BaseModel
from typing import Optional


class EmailIngestRequest(BaseModel):

    message_id: str

    thread_id: str

    sender: str

    subject: str

    body: str

    timestamp: Optional[str] = None