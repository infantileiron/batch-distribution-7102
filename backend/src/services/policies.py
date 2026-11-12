import uuid
from fastapi import HTTPException
from sqlalchemy import select
from src.models import KernelPolicy
from src.utils.serialization import serialize
from src.utils.time import now

def create(db,payload):
 if db.scalar(select(KernelPolicy).where(KernelPolicy.name==payload.name)):raise HTTPException(409,'检验口径名称已存在')
 item=KernelPolicy(id=str(uuid.uuid4()),created_at=now(),**payload.model_dump());db.add(item);db.commit();return serialize(item)
