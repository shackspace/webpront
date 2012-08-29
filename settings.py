from yaml import safe_load

class PrinterDeviceSettings(object):
    def __init__(self, raw):
        if 'includes' in raw:
            self.includes = raw['includes']
        else:
            self.includes = []
        if 'excludes' in raw:
            self.excludes= raw['excludes']
        else:
            self.excludes = []

class PrinterSettings(object):
    def __init__(self, raw):
        if 'devices' in raw:
            self.devices = PrinterDeviceSettings(raw['devices'])
        else:
            self.devices = PrinterDeviceSettings([])
        if 'bauds' in raw:
            self.bauds = raw['bauds']
        else:
            self.bauds = []

class DescriptionSettings(object):
    def __init__(self, raw, default):
        if 'type' in raw:
            if raw['type'] in ['plain', 'markdown']:
                self.type = raw['type']
            else:
                print ("ERROR in config: '" + raw['type'] +
                       "' is not a valid greeting type!")
                self.type = "plain"
        else:
            self.type = "plain"
        if 'text' in raw:
            if self.type == 'markdown':
                import markdown
                self.text = markdown.markdown(raw['text'])
            else:
                self.text = raw['text']
        else:
            self.text = default

class CoreSettings(object):
    def __init__(self, raw):
        if 'printer' in raw:
            self.printer = PrinterSettings(raw['printer'])
        else:
            self.printer = PrinterSettings([])
        self.greeting = DescriptionSettings(raw['greeting'] if 'greeting' in raw else [], """
            <h1>WebPront</h1><p>Welcome to WebPront!</p>
        """)
        if 'name' in raw:
            self.name = raw['name']
        else:
            self.name = 'WebPront'
        self.about = DescriptionSettings(raw['about'] if 'about' in raw else [],"""
            <h2>About</h2>
            <p>This is <strong>WebPront</strong>, a web frontend for
            <a href="https://github.com/kliment/Printrun">PrintRun</a>.
        """
        )
        if 'cookie_secret' in raw:
            self.cookie_secret = raw['cookie_secret']
        else:
            print "WARNING: No cookie_secret set, using default secret"
            self.cookie_secret = "Ifw1Mp4pQAe2SGWlAddMFAQrXoKOiEGTgcEZxFlJ9fw="

class Settings(object):
    def __init__(self, raw):
        if 'core' in raw:
            self.core = CoreSettings(raw['core'])
        else:
            self.core = CoreSettings([])

def load_settings():
    stream = file('config.yaml', 'r')
    values = safe_load (stream)
    stream.close()
    return Settings(values)