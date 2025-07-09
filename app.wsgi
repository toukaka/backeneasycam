import sys
import logging

print("_______________App backend: WSGI__________________")

sys.path.insert(0, '/var/www/backend_app')

from app import app as application
#import register
