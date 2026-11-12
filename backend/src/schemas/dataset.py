from pydantic import BaseModel,Field,ConfigDict
class ColorInput(BaseModel):
 model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
 sample_id:str=Field(min_length=1,max_length=31)
 l:float
 a:float
 b:float
class DatasetInput(BaseModel):
 model_config=ConfigDict(extra='forbid')
 name:str=Field(min_length=2,max_length=120)
 source:str=Field(min_length=2,max_length=160)
 batch_a:list[ColorInput]=Field(min_length=4,max_length=120)
 batch_b:list[ColorInput]=Field(min_length=4,max_length=120)
