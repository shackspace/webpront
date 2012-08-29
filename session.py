from datetime import datetime, timedelta
from pronsoleIF import PronsoleInterface

class Session(object):
    ANONYMOUS = ""
    LIFETIME  = timedelta(hours=1)
    
    def __init__(self, settings):
        self.user = Session.ANONYMOUS
        # TODO
        self.can_view = True
        self.can_control = True
        self.update_timeout()
        self.printer_connection = PronsoleInterface()
        self.device_id = -1
        self.stored_notifications = []
    
    def update_timeout(self):
        self.timeout = datetime.now() + Session.LIFETIME
    
    def __del__(self):
        if self.printer_connection.p.online:
            self.printer_connection.p.disconnect()