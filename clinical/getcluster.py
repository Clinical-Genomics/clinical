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
      
    for root, dirs, files in os.walk(pars['CLUSTERBACKUP']):
      for file in files:
        if file.endswith(".tar.gz"):
          runname = file[:-7]
          print runname
          if (os.path.isfile(pars['CLUSTERBACKUP'] + file) and 
              os.path.isfile(pars['CLUSTERBACKUP'] + file + ".md5.txt")):
            inbackupdir = str(1)
          else:
            sys.exit("not "+pars['CLUSTERBACKUP'] + file + " or "+pars['CLUSTERBACKUP'] + file + ".md5.txt")

          rundate = list(runname.split("_")[0])
          rundate = "20"+rundate[0]+rundate[1]+"-"+rundate[2]+rundate[3]+"-"+rundate[4]+rundate[5]
          clusterdict = {'inbackupdir': inbackupdir, 'runname': runname, 'startdate': rundate}
          print clusterdict
    for root, dirs, fils in os.walk(pars['ONTAPEFOLDER']):
      for tapedir in dirs:
        for rot, drs, files in os.walk(pars['ONTAPEFOLDER'] + tapedir):
          textcontent = ""
          tapedate = datetime.datetime.fromtimestamp(9302765)
          for file in files:
            if file.endswith(".txt"):
              with open (pars['ONTAPEFOLDER'] + tapedir + "/" + file, "r") as textfile:
                textcontent += textfile.read()
                curdate = datetime.datetime.fromtimestamp(os.path.getmtime(pars['ONTAPEFOLDER'] + tapedir + "/" + file))
                if curdate > tapedate:
                  tapedate = curdate
          for file in files:
            if file.endswith(".tar.gz"):
              if (os.path.isfile(pars['ONTAPEFOLDER'] + tapedir + "/" + file) and 
                  os.path.isfile(pars['ONTAPEFOLDER'] + tapedir + "/" + file + ".md5.txt")):
                tapeentry = dbc.getprimarykey( 'backuptape', 'tapedir', tapedir )
                if tapeentry['backuptape_id'] == 0:
                  tapeadd = {}
                  tapeadd['tapedir'] = tapedir
                  tapeadd['nametext'] = textcontent
                  tapeadd['tapedate'] = tapedate
                  tapeentry = dbc.sqlinsert('backuptape', tapeadd)

              runname = file[:-7]
              rundate = list(runname.split("_")[0])
              rundate = "20"+rundate[0]+rundate[1]+"-"+rundate[2]+rundate[3]+"-"+rundate[4]+rundate[5]
              tapedict = {'inbackupdir': inbackupdir, 'runname': runname, 'startdate': rundate}
              for tapekey in tapeentry:
                tapedict[tapekey] = tapeentry[tapekey]
              print tapedict
          

exit(0)
