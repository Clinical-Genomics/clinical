#!/usr/bin/env python
# -*- coding: utf-8 -*-
import errno
import sys
import MySQLdb as mysql
import MySQLdb.cursors
import time
import glob
import re
import socket
import os
import select
import psutil
import subprocess

def readconfig( config ):
  """Reads parameters from a config file.

  Args:
    config (str): path to config file
    If config does not exist the default will be used
  
  Returns:
    dict: parameters from the config file (unparsed)
  """
  if os.path.isfile(config):
    Configfile = config
  else:
    Configfile = "/home/hiseq.clinical/.scilifelabrc"
  Params = {}
  with open(Configfile, "r") as Confs:
    for line in Confs:
      if len(line) > 5 and not line[0] == "#":
        line = line.rstrip()
        pv = line.split(" ")
        if len(pv) > 1:
          arg = pv[0]
          pv.pop(0)
          Params[arg] = ' '.join(pv)
        else:
          Params[pv[0]] = pv[1]
  return Params

def create_tunnel(tunnel_cmd):
  ssh_process = subprocess.Popen(tunnel_cmd,  universal_newlines=True,
                                                shell=True,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT,
                                                stdin=subprocess.PIPE)
    # Assuming that the tunnel command has "-f" and "ExitOnForwardFailure=yes", then the 
    # command will return immediately so we can check the return status with a poll().
  while True:
    p = ssh_process.poll()
    if p is not None: break
    time.sleep(1)
  if p == 0:
        # Unfortunately there is no direct way to get the pid of the spawned ssh process, so we'll find it
        # by finding a matching process using psutil.
    current_username = psutil.Process(os.getpid()).username()
    ssh_processes = [proc for proc in psutil.get_process_list() if proc.cmdline() == tunnel_cmd.split() and 
                               proc.username() == current_username]
    if len(ssh_processes) == 1:
      return ssh_processes[0]
    else:
      raise RuntimeError, 'multiple (or zero?) tunnel ssh processes found: ' + str(ssh_processes) 
  else:
    raise RuntimeError, 'Error creating tunnel: ' + str(p) + ' :: ' + str(ssh_process.stdout.readlines())

def dbconnect( Host, Port, Db, User, Passwd): 
  Cnx = mysql.connect(user=User, port=int(Port), host=Host, passwd=Passwd, db=Db, cursorclass=mysql.cursors.DictCursor)
  Cursor = Cnx.cursor()
  return Cnx, Cursor

def dbclose( Cnx, Cursor):
  Cursor.close()
  Cnx.close()
  return

def generalquery( cursor, query ):
  try:
    cursor.execute(query)
  except mysql.IntegrityError, e: 
    print "Error %d: %s" % (e.args[0],e.args[1])
    exit("DB error")
# handle a specific error condition
  except mysql.Error, e:
    print "Error %d: %s" % (e.args[0],e.args[1])
    exit("Syntax error")
# handle a generic error condition
  except mysql.Warning, e:
    exit("MySQL warning")
# handle warnings, if the cursor you're using raises them
  respons = cursor.fetchall()
  return respons 
  
def versioncheck( cursor, dbname, ver ):
  """Checks version of database against str( dbname) and str ( ver )  [normally from the config file]

  Args:
    dbname (str): database name as stored in table version
    ver (str): version string in the format major.minor.patch

  Returns:
    TRUE: if identical
    str: Database name and version from table version if different
  """
  cmd = """ SELECT major, minor, patch, name FROM version ORDER BY time DESC LIMIT 1 """
  cursor.execute(cmd)
  row = cursor.fetchone()
  if row is not None:
    major = row['major']
    minor = row['minor']
    patch = row['patch']
    name = row['name']
  else:
    sys.exit("Incorrect DB, version not found.")
  if (str(major)+"."+str(minor)+"."+str(patch) == ver and dbname == name):
    return 'True'
  else:
    return (name + " "  + str(major) + "." + str(minor) + "." + str(patch))
  
  
def insertorupdate( cnx, cursor, table, column, entry, insertdict ):
  cursor.execute(""" show index from """ + table + """  """)
  indexkey = cursor.fetchone()
  if not indexkey:
    return "Could not get primary key"
  
  cursor.execute(""" SELECT """ + indexkey['Column_name'] + """ FROM """ + table + """ WHERE """ + column + """ = %s """, 
              (entry, ))
  qkey = cursor.fetchone()
  if key:
    print "Entry exists ", key
    setvalue = ""
    for key in insertdict:
      setvalue += key + "='" + insertdict[key] + "', "
    setvalue = " " + setvalue[:-2] + " "
    print setvalue
    print (""" UPDATE """ + table + """ SET """ + setvalue + """ WHERE """ + indexkey['Column_name'] + 
                         """ = '""" + key + """' """)
    try:
      cursor.execute(""" UPDATE """ + table + """ SET """ + setvalue + """ WHERE """ + indexkey['Column_name'] + 
                         """ = '""" + qkey + """' """)
    except mysql.IntegrityError, e: 
      print "Error %d: %s" % (e.args[0],e.args[1])
      exit("DB error")
# handle a specific error condition
    except mysql.Error, e:
      print "Error %d: %s" % (e.args[0],e.args[1])
      exit("Syntax error")
# handle a generic error condition
    except mysql.Warning, e:
      exit("MySQL warning")
# handle warnings, if the cursor you're using raises them
    cnx.commit()
    return True
  else:
    print "Entry not yet added, will be added."
    columns = ""
    values = ""
    for key in insertdict:
      columns += key + ", "
      values += "'" + insertdict[key] + "', "
    columns = " (" + columns[:-2] + ") "
    values = " (" + values[:-2] + ") " 
    print columns, values
    try:
      cursor.execute(""" INSERT INTO """ + table + """  """ + columns + """ VALUES """ + values )
    except mysql.IntegrityError, e: 
      print "Error %d: %s" % (e.args[0],e.args[1])
      exit("DB error")
# handle a specific error condition
    except mysql.Error, e:
      print "Error %d: %s" % (e.args[0],e.args[1])
      exit("Syntax error")
# handle a generic error condition
    except mysql.Warning, e:
      exit("MySQL warning")
# handle warnings, if the cursor you're using raises them
    cnx.commit()
    return cursor.lastrowid

  
