import uuid,csv,io
from sqlalchemy import select
from fastapi import HTTPException
from src.models import Report,ShiftReview,DistributionRun
from src.services.runs import require_completed
from src.utils.serialization import serialize
from src.utils.time import now

def create(db,payload,user):
 require_completed(db,payload.run_id);db.scalar(select(DistributionRun).where(DistributionRun.id==payload.run_id).with_for_update())
 review=db.scalar(select(ShiftReview).where(ShiftReview.run_id==payload.run_id).order_by(ShiftReview.version.desc()))
 if not review or review.decision!='accepted':raise HTTPException(409,'最新分布复核须接受后才能归档')
 if db.scalar(select(Report).where(Report.review_id==review.id)):raise HTTPException(409,'此复核版本已归档')
 item=Report(id=str(uuid.uuid4()),review_id=review.id,published_by=user['email'],created_at=now(),**payload.model_dump());db.add(item);db.commit();return serialize(item)
def export(db,id):
 report=db.get(Report,id)
 if not report:raise HTTPException(404,'归档不存在')
 result=require_completed(db,report.run_id).result;review=db.get(ShiftReview,report.review_id);buf=io.StringIO();writer=csv.DictWriter(buf,['run_id','checksum','review_version','method','statistic','B','seed','extreme_count','denominator','pvalue_unadjusted','scaling','bandwidth','sigma','n_a','n_b']);writer.writeheader()
 for method in ('energy','mmd'):
  r=result[method];tr=result['transform'];writer.writerow({'run_id':report.run_id,'checksum':result['checksum'],'review_version':review.version,'method':method,'statistic':r['statistic'],'B':result['B'],'seed':result['seed'],'extreme_count':r['extreme_count'],'denominator':r['denominator'],'pvalue_unadjusted':r['pvalue'],'scaling':tr['scaling'],'bandwidth':tr['bandwidth'],'sigma':tr['sigma'],'n_a':result['sample_sizes'][0],'n_b':result['sample_sizes'][1]})
 return chr(0xfeff)+buf.getvalue()
