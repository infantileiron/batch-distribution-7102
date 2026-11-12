from pydantic import BaseModel,Field,ConfigDict
from typing import Literal
class ReviewInput(BaseModel):
 model_config=ConfigDict(extra='forbid')
 run_id:str
 note:str=Field(min_length=10,max_length=2000)
 decision:Literal['accepted','needs_changes']
