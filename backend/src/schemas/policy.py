from pydantic import BaseModel,Field,ConfigDict,model_validator
from typing import Literal
class PolicyInput(BaseModel):
 model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
 name:str=Field(min_length=2,max_length=120)
 scaling:Literal['none','pooled_std']
 bandwidth:Literal['fixed','pooled_median']
 sigma:float|None=Field(default=None,gt=0)
 permutations:int=Field(ge=19,le=999,strict=True)
 seed:int=Field(ge=0,le=2147483647,strict=True)
 @model_validator(mode='after')
 def fixed_width(self):
  if self.bandwidth=='fixed' and self.sigma is None:raise ValueError('固定核宽须明确正sigma')
  if self.bandwidth=='pooled_median' and self.sigma is not None:raise ValueError('自动核宽请留空sigma，避免混淆口径')
  return self
