
#app/models.py

from pydantic import BaseModel
from typing import List, Dict, Optional

class Observation(BaseModel):
    ticket_id: str
    customer_message: str
    history: List[str]
    known_info: Dict
    #missing_info: List[str]
    status: str
    step_count: int
    remaining_steps: int


class Action(BaseModel):
    action_type: str
    content: Optional[str] = ""
    metadata: Optional[Dict] = {}


class Reward(BaseModel):
    value: float
    reason: str