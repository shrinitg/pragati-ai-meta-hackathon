from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel


class InputMessageType(Enum):
    TEXT = "text"
    OPTION = "option"
    AUDIO = "audio"


DefaultTypes = Union[str, dict, int, float]


class InputMessage(BaseModel):
    type: Optional[InputMessageType]
    content: Optional[DefaultTypes]


class AgentInstanceDetails(BaseModel):
    agent_id: str
    session_id: str
    agent_name: Optional[str] = None


class UserData(BaseModel):
    is_first_query: Optional[bool] = True
    supervisor: Optional[AgentInstanceDetails] = None
    current_task_agent: Optional[AgentInstanceDetails] = None


class AgentDetails(BaseModel):
    agent_name: Optional[str]
    instructions: Optional[str]
    tools: Optional[list]
