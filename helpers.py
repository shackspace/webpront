import os, glob, sys
from hashlib import sha256
import random
from time import gmtime, time

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

def generate_session_id():
    return sha256(str(int(time()) + random.random())).hexdigest()

class Tee(object):
    def __init__(self, target):
        self.stdout = sys.stdout
        sys.stdout = self
        self.target=target
    def __del__(self):
        sys.stdout = self.stdout
    def write(self, data):
        self.target(data)
        self.stdout.write(data.encode("utf-8"))
    def flush(self):
        self.stdout.flush()