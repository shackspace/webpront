#/usr/bin/env python

import tornado.ioloop
import tornado.web
import tornado.websocket
import os
from session import Session

import helpers
import globals

class BaseHandler(tornado.web.RequestHandler):
    INFO = 0
    WARNING = 1
    ERROR = 2
    
    def prepare(self):
        globals.delete_expired_objects()
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
            uid = helpers.generate_random_hash()
            self.set_secure_cookie("sessionid", uid)
        if uid not in globals.sessions:
            globals.sessions[uid] = Session(globals.settings)
            globals.sessions[uid].uid = uid
        globals.sessions[uid].refreshTimeout()
        return globals.sessions[uid]
    
    def write_error(self, status_code, **kwargs):
        self.render("templates/error.html", error_code=status_code)
        
    def redirect(self, url, permanent=False, status=None):
        if self.current_user:
            self.current_user.stored_notifications = self.notifications
        super(BaseHandler, self).redirect(url, permanent=permanent, status=status)

class MainHandler(BaseHandler):
    def get(self):
        if self.current_user.pronsole.p.printer:
            connection_id = helpers.generate_random_hash()
            globals.ws_handles[connection_id] = self.current_user
            self.render("templates/interface.html",
                        device=self.current_user.pronsole.p.port,
                        baud=self.current_user.pronsole.p.baud,
                        identify=connection_id)
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
            self.add_notification(BaseHandler.WARNING, "Device is in use by another user.")
        else:
            if self.current_user.pronsole.p.printer:
                self.current_user.pronsole.p.disconnect()
                del globals.device_occupations[self.current_user.device_id]
            try:
                self.current_user.pronsole.p.connect(globals.devices[device_id], baud)
                self.current_user.device_id = device_id
                globals.device_occupations[device_id] = True
            except:
                self.add_notification(BaseHandler.ERROR, "Could not connect to device!")
        self.get()

class DisconnectHandler(BaseHandler):
    def get(self, reason):
        if self.current_user.pronsole.p.printer:
            self.current_user.pronsole.p.disconnect()
            del globals.device_occupations[self.current_user.device_id]
            if reason == "user":
                self.add_notification(BaseHandler.INFO, "Successfully disconnected from printer.")
            elif reason == "lostConnection":
                self.add_notification(BaseHandler.ERROR, "You lost the connection to the server.")
        else:
            self.add_notification(BaseHandler.WARNING, "You are not connected to a printer.")
        self.redirect("/")

class AboutHandler(BaseHandler):
    def get(self):
        self.render("templates/about.html", about=globals.settings.core.about.text)


class WebsocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, uid):
        if uid in globals.ws_handles:
            self.session = globals.ws_handles[uid]
            print "Websocket opened for connection %s" % self.session.uid
            self.session.pronsole.set_output_handler(self, WebsocketHandler.catchprint)
        else:
            print "Denying connection for %s" % uid
            self.session = None
            self.close()
    
    def on_message(self, message):
        if self.session:
            self.write_message(message)
            self.session.pronsole.onecmd(message)
    
    def catchprint(self,l):
        if self:
            self.write_message(l)
        
    def on_close(self):
        self.session.pronsole.set_output_handler(None, None)
        print "Websocket closed for connection %s" % (self.session.uid
                                                      if self.session else "[unknown]")
        self.t = None

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": globals.settings.core.cookie_secret
}

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/about", AboutHandler),
    (r"/disconnect/(.*)", DisconnectHandler),
    (r"/direct/(.*)", WebsocketHandler)
], **settings)

if __name__ == "__main__":
    try:
        application.listen(8888)
        tornado.ioloop.IOLoop.instance().start()
    except:
        print "Closing connections"
        # If we end up here, we need to close all open connections
        for key, session in globals.sessions.iteritems():
            if session.pronsole.p.printer:
                session.pronsole.p.disconnect()