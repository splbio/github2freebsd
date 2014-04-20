from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from sqlalchemy import Column, Integer, String, DateTime, Sequence

class PullRecord(Base):
    __tablename__ = 'pullrequest'

    id = Column(Integer, Sequence('pr_id_seq'), primary_key=True)
    state = Column(Integer, nullable=False, default=0)
    pr = Column(Integer)
    prsubmitted = Column(DateTime)
    headhash = Column(String(40))
