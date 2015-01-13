#!/usr/bin/python
#
import sys
import datetime
import time
import glob
import re
import socket
import os
import select
from dbaccess import *
import subprocess
import psutil

runfolder = sys.argv[1]

if (len(sys.argv)>2):
  configfile = sys.argv[2]
else:
  configfile = 'None'
pars = readconfig(configfile)

if not os.path.isdir(pars['RUNFOLDER'] + runfolder):
  sys.exit("No directory " + pars['RUNFOLDER'] + runfolder)

tunnel_pid = create_tunnel(pars['TUNNELCMD'])

cnx, cursor = dbconnect(pars['CLINICALDBHOST'], pars['CLINICALDBPORT'], pars['STATSDB'], 
                        pars['CLINICALDBUSER'], pars['CLINICALDBPASSWD'])

ver = versioncheck(cursor, pars['STATSDB'], pars['DBVERSION'])

if not ver == 'True':
  print "Wrong db " + ver
  dbclose(cnx, cursor)
  tunnel_pid.terminate()
  exit(0) 

starttonas = datetime.datetime.fromtimestamp(os.path.getmtime(rundir + "/RunInfo.xml" ))
endtonas = datetime.datetime.fromtimestamp(os.path.getmtime(rundir + "/RTAComplete.txt" ))
nas = socket.gethostname()
nasdir = pars['RUNFOLDER']
  
nasdict = {'starttonas': starttonas, 'endtonas': endtonas, 'nas': nas, 'nasdir': nasdir}

res = insertorupdate( cursor, "backup", "runname", pars['RUNFOLDER'], nasdict )
print res

dbclose(cnx, cursor)
tunnel_pid.terminate()
exit(0)
