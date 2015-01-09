#!/usr/bin/python
#
#
import sys
import MySQLdb as mysql
import time
import glob
import re
import socket
import os
import select
import clinicaldb

pars = readconfig()
print pars[''CLINICALDBUSER']

exit(0)
