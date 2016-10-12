""" Test script used to query the db programmatically

"""


import sys
import os
import optparse
import logging
import string
import collections

from fixrgraph.db.isodb import IsoDb
import sqlalchemy


if (len(sys.argv) != 2):
    print "Not enough param"
db_path=sys.argv[1]

if (not os.path.isfile(db_path)):
    print "db does not exist"
    sys.exit(0)


db = IsoDb(db_path)


def get_query_res(db, query):
    res = db.engine.execute(query)
    return res.fetchone()


print os.path.basename(db_path)


db.engine.execute("update logs set user_time = 0.01 where user_time = 0 and status = \"ok\"")

res=get_query_res(db, "SELECT count(isos.id) from isos")
isos=res[0]
print "Total iso: %d" % (isos)

res=get_query_res(db, "SELECT count(logs.id) from logs")
logs=res[0]
print "Num of logs: %d" % (logs)

if (isos != logs):
    print "--- WARNING: logs and isos are different ---"

res=get_query_res(db, "SELECT count(logs.id),sum(logs.user_time),avg(logs.user_time) from logs inner join isos on isos.id = logs.idiso where logs.status = \"ok\"")
solved=res[0]
print "Solved iso: %d" % (solved)
print "Tot time: %f" % (res[1])
print "Avg for iso %f" % (res[2])

res=get_query_res(db, "SELECT count(logs.id) from logs inner join isos on isos.id = logs.idiso where logs.status = \"to\"")
to=res[0]
print "Tot to:  %d" % (to)

if (solved + to != isos):
    print "--- WARNING: solved + to (%d) is different from isos (%d)---" % (solved+to, isos)



#db.engine.execute("DELETE from logs")

#db.engine.execute("DELETE from isos")


# db.engine.execute("DELETE from logs where logs.id in "\
#                   "(SELECT logs.id from logs " \
#                   "inner join isos on  (isos.id = logs.idiso) " \
#                   "where isos.isoname >= \"be.\" and isoname <= \"c\")")

# db.engine.execute("DELETE from isos where isos.isoname >= \"be.\" and isoname <= \"c\"")



