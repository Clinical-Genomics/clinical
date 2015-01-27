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
    configfile = config
  else:
    configfile = "/home/hiseq.clinical/.scilifelabrc"
  params = {}
  with open(configfile, "r") as confs:
    for line in confs:
      if len(line) > 5 and not line[0] == "#":
        line = line.rstrip()
        pv = line.split(" ")
        if len(pv) > 1:
          arg = pv[0]
          pv.pop(0)
          params[arg] = ' '.join(pv)
        else:
          params[pv[0]] = pv[1]
  return params

class create_tunnel(object):

    def __init__(self, tunnel_cmd):
        """Opens an ssh tunnel as defined by the tunnel_cmd

        Args:
          tunnel_cmd (str): tunnel_cmd
          E.g. "ssh -fN -L 1231:localhost:2345 user@ssh.server.com"
        """

        self.tunnelcmd = tunnel_cmd
        ssh_process = subprocess.Popen(tunnel_cmd,  universal_newlines=True, shell=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
        while True:
          p = ssh_process.poll()
          if p is not None: break
          time.sleep(1)
        if p == 0:
          current_username = psutil.Process(os.getpid()).username()
          ssh_processes = [proc for proc in psutil.get_process_list() if proc.cmdline() == tunnel_cmd.split() and 
                         proc.username() == current_username]
          if len(ssh_processes) == 1:
            self.pid = ssh_processes[0]
          else:
            raise RuntimeError, 'multiple (or zero?) tunnel ssh processes found: ' + str(ssh_processes) 
        else:
          raise RuntimeError, 'Error creating tunnel: ' + str(p) + ' :: ' + str(ssh_process.stdout.readlines())

    def __enter__(self):
      return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
      if exc_type:
        print '__exit__(%s, %s, %s)' % (exc_type, exc_val, exc_tb)
      self.pid.terminate()
        
class dbconnect(object):

  def __init__(self, Host, Port, Db, User, Passwd):
    self.cnx = mysql.connect(user=User, port=int(Port), host=Host, passwd=Passwd, db=Db, cursorclass=mysql.cursors.DictCursor)
    self.cursor = self.cnx.cursor()

  def __enter__(self):
#      print '__enter__()'
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    if exc_type:
      print '__exit__(%s, %s, %s)' % (exc_type, exc_val, exc_tb)
    self.cursor.close()
    self.cnx.close()

  def generalquery( self, query ):
    try:
      self.cursor.execute(query)
    except mysql.IntegrityError, e: 
      print "Integrity Error %d: %s" % (e.args[0],e.args[1])
      exit("DB error")
# handle a specific error condition
    except mysql.Error, e:
      print "Generic Error %d: %s" % (e.args[0],e.args[1])
      exit("Syntax error")
# handle a generic error condition
    except mysql.Warning, e:
      exit("MySQL warning")
# handle warnings, if the cursor you're using raises them
    respons = self.cursor.fetchall()
    return respons 
  
  def versioncheck( self, dbname, ver ):
    """Checks version of database against str( dbname) and str ( ver )  [normally from the config file]

    Args:
      dbname (str): database name as stored in table version
      ver (str): version string in the format major.minor.patch

    Returns:
      TRUE: if identical
      str: Database name and version from table version if different
    """
    cmd = """ SELECT major, minor, patch, name FROM version ORDER BY time DESC LIMIT 1 """
    self.cursor.execute(cmd)
    row = self.cursor.fetchone()
    if row is not None:
      major = row['major']
      minor = row['minor']
      patch = row['patch']
      name = row['name']
    else:
      sys.exit("Incorrect DB, version not found.")
    if ('{0}.{1}.{2}'.format(str(major), str(minor), str(patch)) == ver and dbname == name):
      return 'True'
    else:
      return ('{3} {0}.{1}.{2}'.format(str(major), str(minor), str(patch), name))
  
  def insertorupdate( self, table, column, entry, insertdict ):
    self.cursor.execute(""" show index from """ + table + """  """)
    indexkey = self.cursor.fetchone()
    if not indexkey:
      return "Could not get primary key"
  
    self.cursor.execute(' SELECT {0} FROM {1} WHERE {2} = \'{3}\' '.format(indexkey['Column_name'], table, column, entry, ))
    key = self.cursor.fetchone()
    if key:
      print "Entry exists ", key
      setvalues = ""
      for dictkey in insertdict:
        setvalues += dictkey + "='" + str(insertdict[dictkey]) + "', "
      setvalues = " " + setvalues[:-2] + " "
      print setvalues
      uquery = (' UPDATE {0} SET {1} WHERE {2} = \'{3}\' '.format(table, setvalues, indexkey['Column_name'], 
                key[indexkey['Column_name']]))
      try:
        self.cursor.execute(uquery)
      except mysql.IntegrityError, e: 
        print "Integrity Error %d: %s" % (e.args[0],e.args[1])
        exit("DB error")
# handle a specific error condition
      except mysql.Error, e:
        print "Generic Error %d: %s" % (e.args[0],e.args[1])
        exit("Syntax error")
# handle a generic error condition
      except mysql.Warning, e:
        exit("MySQL warning")
# handle warnings, if the cursor you're using raises them
      self.cnx.commit()
      return True
    else:
      print "Entry not yet added, will be added."
      columns = ""
      values = ""
      for dictkey in insertdict:
        columns += dictkey + ", "
        values += "'" + str(insertdict[dictkey]) + "', "
      columns = " (" + columns[:-2] + ") "
      values = " (" + values[:-2] + ") " 
      print columns, values
      try:
        self.cursor.execute(' INSERT INTO {0} {1} VALUES {2} '.format(table, columns, values, ))
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
      self.cnx.commit()
      return self.cursor.lastrowid

  def getprimarykey( self, table, column, entry ):
    """ Extract primary key from unique table entry

        Args:
          table name, column name, entry
          E.g. 'backup', 'starttonas', '2014-12-10 15:15:09'
      
        Returns:
          dict: { columnname: primarykey }
    """
    self.cursor.execute(""" SHOW INDEX FROM """ + table + """ WHERE Key_name = 'PRIMARY' """)
    indexkey = self.cursor.fetchone()
    if not indexkey:
      print "Could not get primary key"
    self.cursor.execute(' SELECT {0} FROM {1} WHERE {2} = \'{3}\' '.format(indexkey['Column_name'], table, column, entry, ))
    replys = self.cursor.fetchall()
    if len(replys) == 1:
#      print "Entry exists ", keys[0]
#      for key in replys:
      return replys[0]
    else: 
      print "Could not get single entry key"
      return { replys.keys()[0]: 0 }
  
  def sqlinsert( self, table, entry ):
    """ Inserts entry dictionary into table

        Args:
          table (str), entry (dictionary coresponding to table structure)
      
        Returns:
          dict: { columnname: primarykey }
    """
    self.cursor.execute(""" SHOW INDEX FROM """ + table + """  """)
    indexkey = self.cursor.fetchone()
    if not indexkey:
      print "Could not get primary key"
      return { indexkey['Column_name']: 0 }
    query = (""" INSERT INTO `%s` (`%s`) VALUES (%s) """ % (table, '`,`'.join(entry.keys()),
                 ','.join([ '%s' for x in xrange(len(entry)) ]) ))
    try:
      self.cursor.execute(query, entry.values(), )
    except mysql.IntegrityError, e: 
      print "Error %d: %s" % (e.args[0],e.args[1])
      exit("DB error")
    except mysql.Error, e:
      print "Error %d: %s" % (e.args[0],e.args[1])
      exit("Syntax error")
    except mysql.Warning, e:
      exit("MySQL warning")
    self.cnx.commit()
    key = self.cursor.lastrowid
    if key:
#      print "Entry added ", key
      return { indexkey['Column_name']: key }
    else: 
      print "Entry failed "
      return { indexkey['Column_name']: 0 }
  
