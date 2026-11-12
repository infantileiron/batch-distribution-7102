import uuid
from pydantic import BaseModel,Field,ConfigDict
class RunInput(BaseModel):
 model_config=ConfigDict(extra='forbid')
 study_id:str
class CancelInput(BaseModel):
 model_config=ConfigDict(extra='forbid')
 reason:str=Field(min_length=2,max_length=500)
