import os, glob, sys
from hashlib import sha256
import random
from time import time
from datetime import datetime

def scanserial():
   """scan for available ports. return a list of device names."""
   baselist=[]
   if os.name=="nt":
       try:
           import _winreg
           key=_winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,"HARDWARE\\DEVICEMAP\\SERIALCOMM")
           i=0
           while(1):
               baselist+=[_winreg.EnumValue(key,i)[1]]
               i+=1
       except:
           pass
   return baselist + (glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*') +
                      glob.glob("/dev/tty.*")   + glob.glob("/dev/cu.*") +
                      glob.glob("/dev/rfcomm*"))

random.seed()

def generate_random_hash():
    return sha256(str(int(time()) + random.random())).hexdigest()

class TimeboundObject(object):
    def __init__(self, ttl):
        self.ttl = ttl
        self.refreshTimeout()
    
    def refreshTimeout(self):
        self.timeout = datetime.now() + self.ttl
    
    def isValid(self):
        return datetime.now() < self.timeout