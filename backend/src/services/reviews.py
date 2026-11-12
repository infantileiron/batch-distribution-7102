import uuid
from sqlalchemy import select,func
from src.models import ShiftReview,DistributionRun
from src.services.runs import require_completed
from src.utils.serialization import serialize
from src.utils.time import now

def create(db,payload,user):
 require_completed(db,payload.run_id);db.scalar(select(DistributionRun).where(DistributionRun.id==payload.run_id).with_for_update())
 version=(db.scalar(select(func.max(ShiftReview.version)).where(ShiftReview.run_id==payload.run_id)) or 0)+1
 item=ShiftReview(id=str(uuid.uuid4()),version=version,author=user['email'],created_at=now(),**payload.model_dump());db.add(item);db.commit();return serialize(item)
