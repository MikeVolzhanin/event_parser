from pydantic import BaseModel
from datetime import datetime

class EventModel(BaseModel):
    event_id: str
    source: str
    channel_name: str
    post_date: datetime
    url: str
    raw_text: str

