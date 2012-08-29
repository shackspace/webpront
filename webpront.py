#/usr/bin/env python

import tornado.ioloop
import tornado.web
import os
from datetime import datetime
from session import Session

import helpers
import globals

class BaseHandler(tornado.web.RequestHandler):
    INFO = 0
    WARNING = 1
    ERROR = 2
    
    def prepare(self):
        if self.current_user:
            self.notifications = self.current_user.stored_notifications
            self.current_user.stored_notifications = []
        else:
            self.notifications = []        
    def add_notification(self, level, message):
        self.notifications.append((level, message))
        
    def render(self, template, **kwargs):
        super(BaseHandler, self).render(template,
                                        title=globals.settings.core.name,
                                        notifications = self.notifications,
                                        **kwargs)
    
    def get_current_user(self):
        uid = self.get_secure_cookie("sessionid")
        if not uid:
            uid = helpers.generate_session_id()
            self.set_secure_cookie("sessionid", uid)
        if uid not in globals.sessions or globals.sessions[uid].timeout < datetime.now():
            globals.sessions[uid] = Session(globals.settings)
        return globals.sessions[uid]
    
    def write_error(self, status_code, **kwargs):
        self.render("templates/error.html", error_code=status_code)
        
    def redirect(self, url, permanent=False, status=None):
        if self.current_user:
            self.current_user.stored_notifications = self.notifications
        super(BaseHandler, self).redirect(url, permanent=permanent, status=status)

class MainHandler(BaseHandler):
    def get(self):
        if self.current_user.printer_connection.p.printer:
            self.render("templates/interface.html",
                        device=self.current_user.printer_connection.p.port,
                        baud=self.current_user.printer_connection.p.baud)
        else:
            self.render("templates/connect.html",
                        devices=globals.devices,
                        bauds=globals.settings.core.printer.bauds,
                        greeting=globals.settings.core.greeting.text)
    
    def post(self):
        device_id = int(self.get_argument("device"))
        baud      = self.get_argument("baud")
        if not device_id in globals.devices:
            print "device_id %i does not exist" % device_id
            self.send_error(400)
            return
        if device_id in globals.device_occupations:
            self.add_notification(BaseError.WARNING, "Device is in use by another user.")
        else:
            if self.current_user.printer_connection.p.printer:
                self.current_user.printer_connection.p.disconnect()
                del globals.device_occupations[self.current_user.device_id]
            try:
                self.current_user.printer_connection.p.connect(globals.devices[device_id], baud)
                self.current_user.device_id = device_id
                globals.device_occupations[device_id] = True
            except:
                self.add_notification(BaseHandler.ERROR, "Could not connect to device!")
        self.get()

class DisconnectHandler(BaseHandler):
    def get(self):
        if self.current_user.printer_connection.p.printer:
            self.current_user.printer_connection.p.disconnect()
            del globals.device_occupations[self.current_user.device_id]
            self.add_notification(BaseHandler.INFO, "Successfully disconnected from printer.")
        else:
            self.add_notification(BaseHandler.WARNING, "You are not connected to a printer.")
        self.redirect("/")

class AboutHandler(BaseHandler):
    def get(self):
        self.render("templates/about.html", about=globals.settings.core.about.text)

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": globals.settings.core.cookie_secret
}

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/about", AboutHandler),
    (r"/disconnect", DisconnectHandler)
], **settings)

if __name__ == "__main__":
    try:
        application.listen(8888)
        tornado.ioloop.IOLoop.instance().start()
    except:
        print "Closing connections"
        # If we end up here, we need to close all open connections
        for key, session in globals.sessions.iteritems():
            if session.printer_connection.p.printer:
                session.printer_connection.p.disconnect()