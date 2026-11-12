from sqlalchemy import String,Integer,JSON,ForeignKey,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class DistributionRun(Base):
 __tablename__='distribution_runs'
 id:Mapped[str]=mapped_column(String,primary_key=True)
 study_id:Mapped[str]=mapped_column(ForeignKey('distribution_studies.id'),unique=True)
 status:Mapped[str]=mapped_column(String)
 attempt_no:Mapped[int]=mapped_column(Integer,default=0)
 study_checksum:Mapped[str|None]=mapped_column(String,nullable=True)
 result:Mapped[dict]=mapped_column(JSON,default=dict)
 error:Mapped[str]=mapped_column(Text,default='')
 created_at:Mapped[str]=mapped_column(String)
 updated_at:Mapped[str|None]=mapped_column(String,nullable=True)
class RunAttempt(Base):
 __tablename__='run_attempts'
 __table_args__=(UniqueConstraint('run_id','attempt_no',name='uq_run_attempts_run_no'),)
 id:Mapped[str]=mapped_column(String,primary_key=True)
 run_id:Mapped[str]=mapped_column(ForeignKey('distribution_runs.id'))
 study_id:Mapped[str]=mapped_column(ForeignKey('distribution_studies.id'))
 attempt_no:Mapped[int]=mapped_column(Integer)
 status:Mapped[str]=mapped_column(String)
 cancel_requested_at:Mapped[str|None]=mapped_column(String,nullable=True)
 cancel_reason:Mapped[str|None]=mapped_column(Text,nullable=True)
 error:Mapped[str]=mapped_column(Text,default='')
 result:Mapped[dict]=mapped_column(JSON,default=dict)
 created_at:Mapped[str]=mapped_column(String)
 started_at:Mapped[str|None]=mapped_column(String,nullable=True)
 finished_at:Mapped[str|None]=mapped_column(String,nullable=True)
