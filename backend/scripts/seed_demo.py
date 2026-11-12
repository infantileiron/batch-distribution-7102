import random,json
from sqlalchemy import select,func
from src.config.database import Base,engine,Session
from src.models import User,ColorBatchDataset,KernelPolicy,DistributionStudy,DistributionRun,RunAttempt,ShiftReview,Report
from src.services.analysis import analyze
from src.services.studies import freeze_hash
from src.utils.security import hash_password
from src.utils.time import now
from src.utils.serialization import serialize

def seed():
 Base.metadata.create_all(engine)
 with Session() as db:
  for role in ('admin','analyst','viewer'):
   if not db.get(User,role):db.add(User(id=role,email=role+'@qichuan.demo',password=hash_password('Color2026!'),role=role))
  rng=random.Random(2407);a=[];b=[];center=[68.,12.,18.]
  for i in range(45):
   va=[rng.gauss(0,s) for s in (1.0,.65,.8)];vb=[2.8+rng.gauss(0,.6),2.2+rng.gauss(0,.45),rng.gauss(0,1.6)]
   for sign in (-1,1):
    a.append({'sample_id':f'A{len(a)+1:03}',**{key:round(c+sign*v,6) for key,c,v in zip(('l','a','b'),center,va)}});b.append({'sample_id':f'B{len(b)+1:03}',**{key:round(c+sign*v,6) for key,c,v in zip(('l','a','b'),center,vb)}})
  if not db.get(ColorBatchDataset,'demo-data'):db.add(ColorBatchDataset(id='demo-data',name='绮川·同均值异分布两批色样',source='qichuan_lab_batches_20261112.json',batch_a=a,batch_b=b,created_at=now()));db.flush()
  for id,name,scaling,width,sigma in [('demo-policy','合并总体SD·合并中位核宽','pooled_std','pooled_median',None),('demo-fixed','原始色度·固定sigma3','none','fixed',3.)]:
   if not db.get(KernelPolicy,id):db.add(KernelPolicy(id=id,name=name,scaling=scaling,bandwidth=width,sigma=sigma,permutations=199,seed=2407,created_at=now()))
  db.flush()
  if not db.get(DistributionStudy,'demo-study'):db.add(DistributionStudy(id='demo-study',name='同均值色样·方差与多峰复核',dataset_id='demo-data',policy_id='demo-policy',snapshot={'dataset':serialize(db.get(ColorBatchDataset,'demo-data')),'policy':serialize(db.get(KernelPolicy,'demo-policy'))},created_at=now()));db.flush()
  if not db.get(DistributionRun,'demo-run'):
   snapshot=db.get(DistributionStudy,'demo-study').snapshot;result=analyze(snapshot);now_value=now()
   db.add(DistributionRun(id='demo-run',study_id='demo-study',status='completed',attempt_no=1,study_checksum=freeze_hash(snapshot),result={**result,'run_id':'demo-run','attempt_no':1},error='',created_at=now_value,updated_at=now_value));db.flush()
   db.add(RunAttempt(id='demo-attempt',run_id='demo-run',study_id='demo-study',attempt_no=1,status='completed',error='',result={**result,'run_id':'demo-run','attempt_no':1},created_at=now_value,started_at=now_value,finished_at=now_value));db.flush()
  if not db.get(ShiftReview,'demo-review'):db.add(ShiftReview(id='demo-review',run_id='demo-run',attempt_id='demo-attempt',attempt_no=1,version=1,note='两批原始均值相同而方差和多峰不同；Energy与MMD分别复核，p未多重校正且不是迁移概率。独立可交换假设不覆盖同缸相关样本。',decision='accepted',author='analyst@qichuan.demo',created_at=now()));db.flush()
  if not db.get(Report,'demo-report'):db.add(Report(id='demo-report',run_id='demo-run',attempt_id='demo-attempt',attempt_no=1,review_id='demo-review',title='绮川色样·分布迁移人工复核',published_by='admin@qichuan.demo',created_at=now()))
  db.commit();return {m.__tablename__:db.scalar(select(func.count()).select_from(m)) for m in (User,ColorBatchDataset,KernelPolicy,DistributionStudy,DistributionRun,RunAttempt,ShiftReview,Report)}
if __name__=='__main__':print(json.dumps(seed(),ensure_ascii=False))
