cproj_dir = '/var/www/cproj'
import sys
sys.path.insert(0, cproj_dir )
import os
os.chdir(cproj_dir)
print "cproj.wsgi working directory: {}".format(os.getcwd())
print os.getuid()
from web_ui import app as application
