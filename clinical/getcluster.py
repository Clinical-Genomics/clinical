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

if (len(sys.argv)>2):
  configfile = sys.argv[2]
else:
  configfile = 'None'
pars = readconfig(configfile)


with create_tunnel(pars['TUNNELCMD']):

  with dbconnect(pars['CLINICALDBHOST'], pars['CLINICALDBPORT'], pars['STATSDB'], 
                        pars['CLINICALDBUSER'], pars['CLINICALDBPASSWD']) as dbc:

    ver = dbc.versioncheck(pars['STATSDB'], pars['DBVERSION'])

    if not ver == 'True':
      print "Wrong db " + ver
      exit(0) 
    else:
      print "Correct db"
      
    nasdict = {'starttonas': starttonas, 'endtonas': endtonas, 'nas': nas, 'nasdir': nasdir, 
           'runname': runfolder, 'startdate': rundate}

#    res = dbc.insertorupdate( "backup", "runname", runfolder, nasdict )
#    print res

exit(0)
