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
  key = cursor.fetchone()
  if key:
    print "Entry exists ", key
    setvalue = ""
    for dictkey in insertdict:
      setvalue += dictkey + "='" + insertdict[dictkey] + "', "
    setvalue = " " + setvalue[:-2] + " "
    print setvalue
    print (""" UPDATE """ + table + """ SET """ + setvalue + """ WHERE """ + indexkey['Column_name'] + 
                         """ = '""" + key[indexkey['Column_name']] + """' """)
    try:
      cursor.execute(""" UPDATE """ + table + """ SET """ + setvalue + """ WHERE """ + indexkey['Column_name'] + 
                         """ = '""" + key[indexkey['Column_name']] + """' """)
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
    for dictkey in insertdict:
      columns += dictkey + ", "
      values += "'" + insertdict[dictkey] + "', "
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

  
