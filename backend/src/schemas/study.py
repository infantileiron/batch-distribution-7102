from pydantic import BaseModel,Field,ConfigDict
from typing import Literal
class StudyInput(BaseModel):
 model_config=ConfigDict(extra='forbid')
 name:str=Field(min_length=2,max_length=120)
 dataset_id:str
 policy_id:str
