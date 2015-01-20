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

with create_tunnel(pars['TUNNELCMD']):

  with dbconnect(pars['CLINICALDBHOST'], pars['CLINICALDBPORT'], pars['STATSDB'], 
                        pars['CLINICALDBUSER'], pars['CLINICALDBPASSWD']) as dbc:

    ver = dbc.versioncheck(pars['STATSDB'], pars['DBVERSION'])

    if not ver == 'True':
      print "Wrong db " + ver
      exit(0) 

    nas = socket.gethostname()
    nasdir = pars['RUNFOLDER']
    rundate = list(runfolder.split("_")[0])
    rundate = "20"+rundate[0]+rundate[1]+"-"+rundate[2]+rundate[3]+"-"+rundate[4]+rundate[5]

    nasdict = {'starttonas': starttonas, 'endtonas': endtonas, 'nas': nas, 'nasdir': nasdir, 
           'runname': runfolder, 'startdate': rundate}

#    res = dbc.insertorupdate( "backup", "runname", runfolder, nasdict )
#    print res

exit(0)
