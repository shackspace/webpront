from datetime import timedelta
from pronsoleIF import PronsoleInterface

import helpers

class Session(helpers.TimeboundObject):
    ANONYMOUS = ""
    LIFETIME  = timedelta(hours=1)
    
    def __init__(self, settings):
        super(Session, self).__init__(Session.LIFETIME)
        self.user = Session.ANONYMOUS
        # TODO
        self.can_control = True
        self.pronsole = PronsoleInterface()
        self.device_id = -1
        self.stored_notifications = []
        self.uid = None
    
    def __del__(self):
        if self.pronsole.p.online:
            self.pronsole.p.disconnect()