from sqlalchemy import *
from migrate import *

meta = MetaData()

pullrequest = Table(
    'pullrequest', meta,
    Column('id', Integer, Sequence('pr_id_seq'), primary_key=True),
    Column('state', Integer, nullable=False, default=0),
    Column('pr', Integer),
    Column('prsubmitted', DateTime),
    Column('headhash', String(40)),
)

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta.bind = migrate_engine
    pullrequest.create()

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine
    pullrequest.drop()
    pass
