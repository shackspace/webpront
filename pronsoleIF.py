import pronsole
import sys

class PronsoleInterface(pronsole.pronsole):
    def __init__(self, outputHandler=None):
        self.old_stdout = sys.stdout
        sys.stdout = self
        
        # pronsole isn't a new-style class, so super() doesn't work
        pronsole.pronsole.__init__(self)
        self._outputHandler = outputHandler
    
    def moveXY(self, x, y):
        if x != 0:
            self.onecmd('move X %s' % x)
        if y != 0:
            self.onecmd('move Y %s' % y)
    
    def moveZ(self, z):
        if z != 0:
            self.onecmd('move Z %s' % z)
    
    def write(self, txt):
        if self._outputHandler:
            self._outputHandler(self._outputObject, txt)
        else:
            self.old_stdout.write(txt)
    
    def set_output_handler(self, obj, handler):
        self._outputHandler = handler
        self._outputObject = obj
    
    def __del__(self):
        sys.stdout = self.old_stdout