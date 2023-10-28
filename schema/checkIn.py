from typing import List
from pydantic import BaseModel 
from langchain.schema import BaseMessage
from datetime import datetime

class CheckIn(BaseModel):
    id: str
    user_id: str
    create_time: datetime
    messages: List