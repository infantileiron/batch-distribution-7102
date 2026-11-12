from pydantic import BaseModel,Field,ConfigDict
from typing import Literal
class RunInput(BaseModel):
 model_config=ConfigDict(extra='forbid')
 study_id:str
