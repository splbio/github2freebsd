from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model import PullRecord

from sqlalchemy.sql import func

class Tracking:
    def __init__(self, dbpath="sqlite:///github.db", echo=True):
	self.engine = create_engine(dbpath)
	self.sessionClass = sessionmaker(bind=self.engine)
	self.session = self.sessionClass()
	self.conn = self.engine.connect()

    def get_max_pull_id(self):
	if False:
	    prec = PullRecord()
	    self.session.add(prec)
	    print prec
	    self.session.commit()

	rv = 0
	qry = self.session.query(func.max(PullRecord.id).label("max_id"))
	for _res in qry.all():
	    #print _res
	    rv = _res[0]
	    if rv is None:
		rv = 0
	print rv
        return rv

    def record_pr_sent(self, pull_id):
        prec = PullRecord(id=pull_id, state=0)
        self.session.add(prec)
        self.session.commit()
	

