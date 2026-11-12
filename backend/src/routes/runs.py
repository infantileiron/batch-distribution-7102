from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from src.config.database import db_session
from src.controllers.auth import current_user,writer,admin
from src.models import DistributionRun,RunAttempt
from src.schemas.run import RunInput,CancelInput
from src.services import runs as service
router=APIRouter(prefix='/runs')

@router.get('')
def listing(db=Depends(db_session),user=Depends(current_user)):
 items=db.scalars(select(DistributionRun).order_by(DistributionRun.created_at.desc())).all()
 attempts=db.scalars(select(RunAttempt).order_by(RunAttempt.run_id,RunAttempt.attempt_no.desc())).all()
 grouped={}
 for attempt in attempts:grouped.setdefault(attempt.run_id,[]).append(attempt)
 return [service._detail(item,grouped.get(item.id,[])) for item in items]

@router.post('')
def create(payload:RunInput,db=Depends(db_session),user=Depends(writer)):return service.create(db,payload.study_id)

@router.post('/{id}/retry')
def retry(id:str,db=Depends(db_session),user=Depends(writer)):return service.retry(db,id)

@router.post('/{id}/cancel')
def cancel(id:str,payload:CancelInput,db=Depends(db_session),user=Depends(writer)):return service.cancel(db,id,payload.reason)

@router.get('/{id}')
def detail(id:str,db=Depends(db_session),user=Depends(current_user)):
 run=db.get(DistributionRun,id)
 if not run:raise HTTPException(404,'运行不存在')
 return service.detail(db,id)
