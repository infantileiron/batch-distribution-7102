import uuid
from fastapi import HTTPException
from sqlalchemy import select,func
from src.models import ShiftReview,DistributionRun,RunAttempt
from src.services.runs import require_completed
from src.utils.serialization import serialize
from src.utils.time import now

def create(db,payload,user):
 run=require_completed(db,payload.run_id);db.scalar(select(DistributionRun).where(DistributionRun.id==payload.run_id).with_for_update())
 attempt=db.scalar(select(RunAttempt).where(RunAttempt.run_id==run.id,RunAttempt.attempt_no==run.attempt_no))
 if attempt and attempt.status!='completed':raise HTTPException(409,'当前尝试没有可复核的成功结果')
 version=(db.scalar(select(func.max(ShiftReview.version)).where(ShiftReview.run_id==payload.run_id)) or 0)+1
 item=ShiftReview(id=str(uuid.uuid4()),version=version,attempt_id=attempt.id if attempt else None,attempt_no=attempt.attempt_no if attempt else None,author=user['email'],created_at=now(),**payload.model_dump());db.add(item);db.commit();return serialize(item)
