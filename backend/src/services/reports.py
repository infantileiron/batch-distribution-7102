import uuid,csv,io
from fastapi import HTTPException
from sqlalchemy import select
from src.models import Report,ShiftReview,DistributionRun,RunAttempt
from src.services.runs import require_completed
from src.utils.serialization import serialize
from src.utils.time import now

def create(db,payload,user):
 run=require_completed(db,payload.run_id);db.scalar(select(DistributionRun).where(DistributionRun.id==payload.run_id).with_for_update())
 attempt=db.scalar(select(RunAttempt).where(RunAttempt.run_id==run.id,RunAttempt.attempt_no==run.attempt_no))
 review=db.scalar(select(ShiftReview).where(ShiftReview.run_id==payload.run_id,ShiftReview.decision=='accepted').order_by(ShiftReview.version.desc()))
 if not review or review.decision!='accepted':raise HTTPException(409,'最新分布复核须接受后才能归档')
 if review.attempt_id and (not attempt or review.attempt_id!=attempt.id):raise HTTPException(409,'最新接受复核属于更早的尝试版本，不能归档到当前尝试')
 if db.scalar(select(Report).where(Report.review_id==review.id)):raise HTTPException(409,'此复核版本已归档')
 item=Report(id=str(uuid.uuid4()),review_id=review.id,attempt_id=review.attempt_id,attempt_no=review.attempt_no,published_by=user['email'],created_at=now(),**payload.model_dump());db.add(item);db.commit();return serialize(item)

def _attempt_result(db,report):
 if report.attempt_id:
  attempt=db.get(RunAttempt,report.attempt_id)
  if not attempt or attempt.attempt_no!=report.attempt_no or attempt.status!='completed':raise HTTPException(409,'归档绑定的尝试结果不可用')
  return attempt.result
 return require_completed(db,report.run_id).result

def export(db,id):
 report=db.get(Report,id)
 if not report:raise HTTPException(404,'归档不存在')
 result=_attempt_result(db,report);review=db.get(ShiftReview,report.review_id);buf=io.StringIO();writer=csv.DictWriter(buf,['run_id','attempt_no','checksum','review_version','method','statistic','B','seed','extreme_count','denominator','pvalue_unadjusted','scaling','bandwidth','sigma','n_a','n_b']);writer.writeheader()
 for method in ('energy','mmd'):
  r=result[method];tr=result['transform'];writer.writerow({'run_id':report.run_id,'attempt_no':report.attempt_no if report.attempt_no is not None else result.get('attempt_no',''),'checksum':result['checksum'],'review_version':review.version,'method':method,'statistic':r['statistic'],'B':result['B'],'seed':result['seed'],'extreme_count':r['extreme_count'],'denominator':r['denominator'],'pvalue_unadjusted':r['pvalue'],'scaling':tr['scaling'],'bandwidth':tr['bandwidth'],'sigma':tr['sigma'],'n_a':result['sample_sizes'][0],'n_b':result['sample_sizes'][1]})
 return chr(0xfeff)+buf.getvalue()
