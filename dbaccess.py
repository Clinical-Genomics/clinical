#!/usr/bin/env python
# -*- coding: utf-8 -*-
import errno
import sys
import MySQLdb as mysql
import time
import glob
import re
import socket
import os
import select

def readconfig( config ):
  configfile = "/home/hiseq.clinical/.scilifelabrc"
  params = {}
  with open(configfile, "r") as confs:
    for line in confs:
      if len(line) > 5 and not line[0] == "#":
        line = line.rstrip()
        pv = line.split(" ")
        params[pv[0]] = pv[1]
  return params

def dbconnect( Host, Port, Db, User, Passwd): 
  Cnx = mysql.connect(user=User, port=Port, host=Host, passwd=Passwd, db=Db)
  Cursor = cnx.cursor()
  return Cnx, Cursor

def dbclose( Cnx, Cursor):
  Cursor.close()
  Cnx.close()
  return
