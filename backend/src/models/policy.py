from sqlalchemy import String,Double,Integer,JSON,ForeignKey,Text
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class KernelPolicy(Base):
 __tablename__='kernel_policies'
 id:Mapped[str]=mapped_column(String,primary_key=True)
 name:Mapped[str]=mapped_column(String,unique=True)
 scaling:Mapped[str]=mapped_column(String)
 bandwidth:Mapped[str]=mapped_column(String)
 sigma:Mapped[float|None]=mapped_column(Double,nullable=True)
 permutations:Mapped[int]=mapped_column(Integer)
 seed:Mapped[int]=mapped_column(Integer)
 created_at:Mapped[str]=mapped_column(String)
