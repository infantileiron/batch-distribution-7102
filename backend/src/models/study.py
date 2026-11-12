from sqlalchemy import String,Double,Integer,JSON,ForeignKey,Text
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class DistributionStudy(Base):
 __tablename__='distribution_studies'
 id:Mapped[str]=mapped_column(String,primary_key=True)
 name:Mapped[str]=mapped_column(String,unique=True)
 dataset_id:Mapped[str]=mapped_column(ForeignKey('color_batch_datasets.id'))
 policy_id:Mapped[str]=mapped_column(ForeignKey('kernel_policies.id'))
 snapshot:Mapped[dict]=mapped_column(JSON)
 created_at:Mapped[str]=mapped_column(String)
