import hashlib,json,uuid
from fastapi import HTTPException
from sqlalchemy import select
from src.models import ColorBatchDataset,KernelPolicy,DistributionStudy
from src.utils.serialization import serialize
from src.utils.time import now

def freeze_hash(snapshot):
 return hashlib.sha256(json.dumps(snapshot,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def create(db,payload):
 dataset=db.get(ColorBatchDataset,payload.dataset_id);policy=db.get(KernelPolicy,payload.policy_id)
 if not dataset or not policy:raise HTTPException(404,'批次对照或检验口径不存在')
 if db.scalar(select(DistributionStudy).where(DistributionStudy.name==payload.name)):raise HTTPException(409,'分布研究名称已存在')
 snapshot={'dataset':serialize(dataset),'policy':serialize(policy)}
 item=DistributionStudy(id=str(uuid.uuid4()),snapshot=snapshot,created_at=now(),**payload.model_dump());db.add(item);db.commit();return serialize(item)
