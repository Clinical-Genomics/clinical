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

if (len(sys.argv)>1):
  configfile = sys.argv[1]
else:
  configfile = 'None'
pars = readconfig(configfile)

if not os.path.isdir(pars['BACKUPCOPYFOLDER']):
  sys.exit("No directory " + pars['BACKUPCOPYFOLDER'])

with create_tunnel(pars['TUNNELCMD']):

  with dbconnect(pars['CLINICALDBHOST'], pars['CLINICALDBPORT'], pars['STATSDB'], 
                        pars['CLINICALDBUSER'], pars['CLINICALDBPASSWD']) as dbc:

    ver = dbc.versioncheck(pars['STATSDB'], pars['DBVERSION'])

    if not ver == 'True':
      print "Wrong db " + ver
      exit(0) 

    for root, dirs, files in os.walk(pars['BACKUPCOPYFOLDER']):
      for file in files:
        if file.endswith(".tar.gz"):
          runname = file[:-7]
          print runname
          if (os.path.isfile(pars['BACKUPCOPYFOLDER'] + file) and 
              os.path.isfile(pars['BACKUPCOPYFOLDER'] + file + ".md5.txt")):
            backupdone = str(datetime.datetime.fromtimestamp(os.path.getmtime(pars['BACKUPCOPYFOLDER'] + file )))
            md5done = str(datetime.datetime.fromtimestamp(os.path.getmtime(pars['BACKUPCOPYFOLDER'] + file + ".md5.txt" )))
          else:
            sys.exit("not "+pars['BACKUPCOPYFOLDER'] + file + " or "+pars['BACKUPCOPYFOLDER'] + file + ".md5.txt")
          rundate = list(runname.split("_")[0])
          rundate = "20"+rundate[0]+rundate[1]+"-"+rundate[2]+rundate[3]+"-"+rundate[4]+rundate[5]
          nasdict = {'backupdone': backupdone, 'md5done': md5done, 'runname': runname, 'startdate': rundate}
          res = dbc.insertorupdate( "backup", "runname", runname, nasdict )
          print res

exit(0)
