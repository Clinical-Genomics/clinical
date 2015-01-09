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

HOST="clinical-db.scilifelab.se"
# Ports are handled in ~/.ssh/config since we use OpenSSH
COMMAND="uname -a"
 
# ssh -fN -L 3307:localhost:3306 hiseq.clinical@clinical-db.scilifelab.se
cmnd = ['ssh', '-f', '-N', '-L', '3307:localhost:3306', 'hiseq.clinical@clinical-db.scilifelab.se']
# ["ssh", "%s" % HOST, COMMAND]

ssh = subprocess.Popen(cmnd,
                       shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE
                       )
#result = ssh.stdout.readlines()
#if result == []:
#    error = ssh.stderr.readlines()
#    print >>sys.stderr, "ERROR: %s" % error
#else:
#    print result
print str(ssh.pid)

pars = readconfig('hej')
print pars['CLINICALDBUSER']

cnx, cursor = ssh.communicate(dbconnect(pars['CLINICALDBHOST'], pars['CLINICALDBPORT'], pars['STATSDB'], 
                        pars['CLINICALDBUSER'], pars['CLINICALDBPASSWD']))

_VERSION_ = pars['DBVERSION']
cursor.execute(""" SELECT major, minor, patch FROM version ORDER BY time DESC LIMIT 1 """)
row = cursor.fetchone()
if row is not None:
  major = row[0]
  minor = row[1]
  patch = row[2]
else:
  sys.exit("Incorrect DB, version not found.")
if (str(major)+"."+str(minor)+"."+str(patch) == _VERSION_):
  print pars['STATSDB'] + " Correct database version "+str(_VERSION_)+"   DB "+pars['STATSDB']
else:
  exit (pars['STATSDB'] + "Incorrect DB version. This script is made for "+str(_VERSION_)+" not for "
         +str(major)+"."+str(minor)+"."+str(patch))

dbclose(cnx, cursor)

ssh.kill()

exit(0)
