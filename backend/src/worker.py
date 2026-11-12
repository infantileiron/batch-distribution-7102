from pathlib import Path
import redis,sys,time,traceback
from sqlalchemy import select
from src.config.settings import REDIS_URL
from src.config.database import Session
from src.models import DistributionRun,DistributionStudy,RunAttempt
from src.services.analysis import analyze
from src.services.cancellation import AttemptCancelled,AttemptSuperseded
from src.services.runs import FINAL_STATUSES
from src.services.studies import freeze_hash
from src.utils.time import now
client=redis.Redis.from_url(REDIS_URL);heartbeat=Path('/artifacts/worker-heartbeat')
QUEUE='batch-distribution:jobs'

def _load(run_id,attempt_no):
 with Session() as db:
  return db.scalar(select(RunAttempt).where(RunAttempt.run_id==run_id,RunAttempt.attempt_no==attempt_no))

def _finalize(attempt_id,status,result=None,error=''):
 with Session() as db:
  # Lock the run row first: it is the attempt-ownership token. Reading the attempt
  # afterwards means a retry that committed while we waited is always observed.
  attempt=db.get(RunAttempt,attempt_id)
  if not attempt:return
  run=db.scalar(select(DistributionRun).where(DistributionRun.id==attempt.run_id).with_for_update())
  if run:db.refresh(attempt)
  if not run or run.attempt_no!=attempt.attempt_no or attempt.status in FINAL_STATUSES:
   # Superseded, cancelled, or already finalized: a stale/duplicate delivery must not publish.
   db.rollback();return
  if status=='completed' and attempt.cancel_requested_at:
   status,error='cancelled','已撤销：'+(attempt.cancel_reason or '')
  attempt.status=status;attempt.finished_at=now();attempt.error=error
  if status=='completed':
   attempt.result={**result,'run_id':run.id,'attempt_no':attempt.attempt_no}
   run.result=attempt.result;run.status='completed';run.error=''
  elif status=='failed':
   run.status='failed';run.error=error
  else:
   run.status='cancelled';run.error=error
  run.updated_at=now();db.commit()

def _stop(run_id,attempt_no):
 with Session() as db:
  run=db.scalar(select(DistributionRun).where(DistributionRun.id==run_id))
  attempt=_load(run_id,attempt_no)
  if not run or run.attempt_no!=attempt_no:return ('superseded',None)
  if attempt and attempt.cancel_requested_at:return ('cancelled',attempt.cancel_reason or '')
  return None

def execute(id):
 with Session() as db:
  attempt=db.get(RunAttempt,id)
  if not attempt:return
  if attempt.status=='queued' and attempt.cancel_requested_at:
   _finalize(id,'cancelled',error='已撤销：'+(attempt.cancel_reason or ''));return
  if attempt.status in FINAL_STATUSES:return
  run=db.get(DistributionRun,attempt.run_id)
  if not run or run.attempt_no!=attempt.attempt_no:return
  study=db.get(DistributionStudy,attempt.study_id)
  if not study:
   _finalize(id,'failed',error='分布研究不存在');return
  snapshot=study.snapshot;checksum=freeze_hash(snapshot)
  if run.study_checksum and run.study_checksum!=checksum:
   _finalize(id,'failed',error='冻结研究快照已变化，拒绝使用新口径');return
  # Atomic claim: exactly one delivery moves a queued attempt to running, so duplicates skip.
  claimed=db.execute(select(RunAttempt).where(RunAttempt.id==id,RunAttempt.status=='queued').with_for_update()).scalar_one_or_none()
  if not claimed:
   # A redelivered in-flight attempt after a worker restart resumes with the same ownership token.
   if attempt.status!='running':db.rollback();return
  else:
   claimed.status='running';claimed.started_at=now();run.status='running';run.updated_at=now()
  run_id,attempt_no=run.id,run.attempt_no;db.commit()
 try:
  # Compute outside any DB transaction so cancel/retry are never blocked by the permutation loop.
  # Poll the DB at most every half second; a long B never hammers the connection pool.
  last={'t':0.0}
  def checkpoint():
   if time.monotonic()-last['t']<0.5:return None
   last['t']=time.monotonic();return _stop(run_id,attempt_no)
  result=analyze(snapshot,checkpoint)
 except AttemptCancelled as error:_finalize(id,'cancelled',error='已撤销：'+str(error))
 except AttemptSuperseded as error:
  # A newer attempt (or a run that moved on) owns this record; the old result is discarded.
  print(f'discarded superseded attempt {id}',file=sys.stderr,flush=True);return
 except Exception as error:
  with Session() as db:
   run=db.scalar(select(DistributionRun).where(DistributionRun.id==run_id))
   if run and run.attempt_no!=attempt_no:return
  traceback.print_exc();_finalize(id,'failed',error=str(error))
 else:
  state=_stop(run_id,attempt_no)
  if state is None:_finalize(id,'completed',result=result)
  elif state[0]=='cancelled':_finalize(id,'cancelled',error='已撤销：'+(state[1] or ''))
  # superseded: no finalize; the newer attempt owns the run record.

def run_forever():
 with Session() as db:
  for id in db.scalars(select(RunAttempt.id).where(RunAttempt.status.in_(['queued','running']))).all():
   # Queued attempts plus attempts stranded mid-run by a restart; never cancelled/final ones.
   client.lpush(QUEUE,id)
 while True:
  heartbeat.touch();job=client.brpop(QUEUE,timeout=1)
  if job:execute(job[1].decode())

if __name__=='__main__':run_forever()
