#!/usr/bin/python
#
#
import sys
#import MySQLdb as mysql
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
# print pars['CLINICALDBUSER']

tunnel_pid = create_tunnel(pars['TUNNELCMD'])

cnx, cursor = dbconnect(pars['CLINICALDBHOST'], pars['CLINICALDBPORT'], pars['STATSDB'], 
                        pars['CLINICALDBUSER'], pars['CLINICALDBPASSWD'])

ver = versioncheck(pars['STATSDB'], pars['DBVERSION'])

if not ver == 'True':
  print "Wrong db " + ver
  dbclose(cnx, cursor)
  tunnel_pid.terminate()
  exit(0) 

res = insertorupdate( cursor, "backup", "runname", "141215_D00134_0167_AHB0VJADXX", [] )

dbclose(cnx, cursor)

tunnel_pid.terminate()

exit(0)
