from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class PromptCreate(BaseModel):
    prompt: str

class PromptOut(BaseModel):
    prompt: str
    response: str
    timestamp: datetime

    model_config = {
        "from_attributes": True  # Replaces `orm_mode = True` in Pydantic v2
    }