import pronsole

class PronsoleInterface(pronsole.pronsole):
    def moveXY(self, x, y):
        if x != 0:
            self.onecmd('move X %s' % x)
        if y != 0:
            self.onecmd('move Y %s' % y)
    
    def moveZ(self, z):
        if z != 0:
            self.onecmd('move Z %s' % z)