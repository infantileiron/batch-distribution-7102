import uuid
from fastapi import HTTPException
from sqlalchemy import select
from src.models import ColorBatchDataset
from src.services.validation import validate_dataset
from src.utils.serialization import serialize
from src.utils.time import now

def create(db,payload):
 data=payload.model_dump()
 try:validate_dataset(data['batch_a'],data['batch_b'])
 except ValueError as e:raise HTTPException(422,str(e))
 if db.scalar(select(ColorBatchDataset).where(ColorBatchDataset.name==payload.name)):raise HTTPException(409,'批次对照名称已存在')
 item=ColorBatchDataset(id=str(uuid.uuid4()),created_at=now(),**data);db.add(item);db.commit();return serialize(item)
