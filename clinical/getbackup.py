#!/usr/bin/python
#
#
import sys
import MySQLdb as mysql
import time
import glob
import re
import socket
import os
import select
from dbaccess import *
import subprocess
import psutil

# ssh -fN -L 3307:localhost:3306 hiseq.clinical@clinical-db.scilifelab.se
cmnd = 'ssh -fN -L 3307:localhost:3306 hiseq.clinical@clinical-db.scilifelab.se'

tunnel_pid = create_tunnel(cmnd)

pars = readconfig('hej')
print pars['CLINICALDBUSER']

cnx, cursor = dbconnect(pars['CLINICALDBHOST'], pars['CLINICALDBPORT'], pars['STATSDB'], 
                        pars['CLINICALDBUSER'], pars['CLINICALDBPASSWD'])

cmd = """ SELECT major, minor, patch FROM version ORDER BY time DESC LIMIT 1 """

_VERSION_ = pars['DBVERSION']
cursor.execute(cmd)
row = cursor.fetchone()
if row is not None:
  print str(row[0])
  major = row[0].major
  minor = row.minor
  patch = row.patch
else:
  sys.exit("Incorrect DB, version not found.")
if (str(major)+"."+str(minor)+"."+str(patch) == _VERSION_):
  print pars['STATSDB'] + " Correct database version "+str(_VERSION_)+"   DB "+pars['STATSDB']
else:
  exit (pars['STATSDB'] + "Incorrect DB version. This script is made for "+str(_VERSION_)+" not for "
         +str(major)+"."+str(minor)+"."+str(patch))

cmd2 = """ SELECT major, minor, patch FROM version ORDER BY time """
results = generalquery(cursor, cmd2)
for res in results:
  print str(res)

dbclose(cnx, cursor)

#p = ssh_process.poll()
#print str(p), tunnel_pid
tunnel_pid.terminate()

exit(0)
