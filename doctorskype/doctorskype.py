import dbus

class DbusChecker(object):

    def __init__(self, name='DoctorSkype')
        self.name = name
        self.skype = None

    def connect(self):
        bus = dbus.SessionBus()
        proxy = dbus.get_object('com.Skype.API', '/com/Skype')
        self.skype = dbus.Interface(proxy, 'com.Skype.API')
        self.skype.Invoke('#A NAME ' + self.name)
        self.skype.Invoke('#A PROTOCOL 8')

    def check(self):
        if self.skype is None:
            self.connect()
        result = self.skype.Invoke ('#A GET USERSTATUS')
        temp = 'AWAY' if result != 'AWAY' else 'INVISIBLE'
        res2 = self.skype.Invoke('#B SET USERSTATUS ' + temp)
        res3 = self.skype.Invoke('#C SET USERSTATUS ' + result)
     
        if res3 != '#C USERSTATUS ' + result:
            self._restart_skype()

    def _restart_skype(self):
        import psi
        
