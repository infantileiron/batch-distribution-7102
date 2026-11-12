import uuid,redis
from fastapi import HTTPException
from src.models import DistributionRun,DistributionStudy
from src.config.settings import REDIS_URL
from src.utils.time import now
from src.utils.serialization import serialize

def create(db,study_id):
 if not db.get(DistributionStudy,study_id):raise HTTPException(404,"分布研究不存在")
 item=DistributionRun(id=str(uuid.uuid4()),study_id=study_id,status='queued',result={},error='',created_at=now());db.add(item);db.commit()
 try:redis.Redis.from_url(REDIS_URL).lpush('batch-distribution:jobs',item.id)
 except redis.RedisError:
  item.status='failed';item.error='队列不可用，请重试';db.commit();raise HTTPException(503,item.error)
 return serialize(item)
def require_completed(db,id):
 item=db.get(DistributionRun,id)
 if not item:raise HTTPException(404,'运行不存在')
 if item.status!='completed':raise HTTPException(409,'运行尚未成功完成')
 return item
