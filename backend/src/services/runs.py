import uuid,redis
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from src.models import DistributionRun,DistributionStudy,RunAttempt
from src.config.settings import REDIS_URL
from src.services.studies import freeze_hash
from src.utils.time import now
from src.utils.serialization import serialize

FINAL_STATUSES=('completed','failed','cancelled')
ACTIVE_STATUSES=('queued','running')

def _enqueue(id):
 try:redis.Redis.from_url(REDIS_URL).lpush('batch-distribution:jobs',id)
 except redis.RedisError:return False
 return True

def _new_attempt(db,run,no):
 item=RunAttempt(id=str(uuid.uuid4()),run_id=run.id,study_id=run.study_id,attempt_no=no,status='queued',error='',result={},created_at=now());db.add(item);return item

def _attempt_rows(db,run_id):
 return db.scalars(select(RunAttempt).where(RunAttempt.run_id==run_id).order_by(RunAttempt.attempt_no.desc())).all()

def _begin(db,run,no):
 """Append the next attempt and point the run record at it; the caller commits."""
 attempt=_new_attempt(db,run,no)
 run.attempt_no=no;run.status='queued';run.error='';run.result={};run.updated_at=now()
 return attempt

def _submit(db,run,attempt):
 db.commit()
 if _enqueue(attempt.id):return serialize(run)
 attempt.status='failed';attempt.error='队列不可用，请重试';attempt.finished_at=now();run.status='failed';run.error=attempt.error;run.updated_at=now();db.commit()
 raise HTTPException(503,attempt.error)

def create(db,study_id):
 study=db.get(DistributionStudy,study_id)
 if not study:raise HTTPException(404,'分布研究不存在')
 if db.scalar(select(DistributionRun).where(DistributionRun.study_id==study_id)) is not None:
  raise HTTPException(409,'该研究已有检验任务记录；失败或撤销请在原记录重试，新口径请冻结新研究')
 item=DistributionRun(id=str(uuid.uuid4()),study_id=study_id,status='queued',attempt_no=0,study_checksum=freeze_hash(study.snapshot),result={},error='',created_at=now(),updated_at=now());db.add(item)
 try:db.flush()
 except IntegrityError:
  db.rollback();raise HTTPException(409,'该研究已有检验任务记录；失败或撤销请在原记录重试，新口径请冻结新研究')
 return _submit(db,item,_begin(db,item,1))

def retry(db,run_id):
 item=db.scalar(select(DistributionRun).where(DistributionRun.id==run_id).with_for_update())
 if not item:raise HTTPException(404,'运行不存在')
 if item.status in ACTIVE_STATUSES:
  attempt=db.scalar(select(RunAttempt).where(RunAttempt.run_id==run_id,RunAttempt.attempt_no==item.attempt_no,RunAttempt.status.in_(ACTIVE_STATUSES)).with_for_update())
  if not attempt or not attempt.cancel_requested_at:raise HTTPException(409,'当前尝试尚未结束；请先撤销，再发起重试')
  # The cancel is already registered, so the old attempt is closed here; the worker discards its result.
  attempt.status='cancelled';attempt.finished_at=now();attempt.error='已撤销：'+(attempt.cancel_reason or '');item.status='cancelled';item.error=attempt.error
 elif item.status not in ('failed','cancelled'):raise HTTPException(409,'仅失败或已撤销的尝试可重试')
 study=db.get(DistributionStudy,item.study_id)
 if not study:raise HTTPException(404,'分布研究不存在')
 current=freeze_hash(study.snapshot)
 if item.study_checksum and item.study_checksum!=current:raise HTTPException(409,'冻结研究快照与任务创建时不一致，拒绝重试')
 item.study_checksum=item.study_checksum or current
 return _submit(db,item,_begin(db,item,(item.attempt_no or 0)+1))

def cancel(db,run_id,reason):
 item=db.scalar(select(DistributionRun).where(DistributionRun.id==run_id).with_for_update())
 if not item:raise HTTPException(404,'运行不存在')
 attempt=db.scalar(select(RunAttempt).where(RunAttempt.run_id==run_id,RunAttempt.attempt_no==item.attempt_no).with_for_update())
 if not attempt or attempt.status not in ACTIVE_STATUSES:raise HTTPException(409,'当前尝试已结束，无法撤销')
 if attempt.cancel_requested_at:raise HTTPException(409,'撤销已登记，等待当前计算结束')
 # When a retry already closed this attempt and moved the run on, the cancel is a late
 # confirmation only: stamp the old attempt, never reopen or retarget the newer one.
 attempt.cancel_requested_at=now();attempt.cancel_reason=reason
 if item.attempt_no!=attempt.attempt_no:
  item.updated_at=now();db.commit();return {**serialize(item),'cancel_pending':False}
 if attempt.status=='queued':
  attempt.status='cancelled';attempt.error='已撤销：'+reason;attempt.finished_at=now();item.status='cancelled';item.error=attempt.error
 item.updated_at=now();db.commit()
 return {**serialize(item),'cancel_pending':attempt.status=='running'}

def _summary(attempt):
 result=attempt.result
 if not result:return None
 return {'run_id':attempt.run_id,'attempt_no':attempt.attempt_no,'stats':{method:{key:result[method][key] for key in ('statistic','pvalue','extreme_count','denominator')} for method in ('energy','mmd')},'B':result.get('B'),'seed':result.get('seed'),'checksum':result.get('checksum'),'sample_sizes':result.get('sample_sizes')}

def _detail(item,attempts):
 rows=[]
 for attempt in attempts:
  row=serialize(attempt);row.pop('result',None);row['current']=attempt.attempt_no==item.attempt_no;row['result_published']=bool((attempt.result or {}).get('run_id'));row['result_summary']=_summary(attempt) if attempt.result else None
  rows.append(row)
 current=next((row for row in rows if row['current']),None)
 return {**serialize(item),'attempts':rows,'current_attempt':current,'cancel_pending':bool(current and current['status']=='running' and current['cancel_requested_at'])}

def detail(db,id,attempts=None):
 item=db.get(DistributionRun,id)
 if not item:raise HTTPException(404,'运行不存在')
 return _detail(item,_attempt_rows(db,id) if attempts is None else attempts)

def require_completed(db,id):
 item=db.get(DistributionRun,id)
 if not item:raise HTTPException(404,'运行不存在')
 if item.status!='completed':raise HTTPException(409,'运行尚未成功完成')
 return item
