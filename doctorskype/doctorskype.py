import dbus
from dbus.exceptions import DBusException
import subprocess
import psi
import psi.process
import time
 
class DbusChecker(object):

    def __init__(self, name='DoctorSkype'):
        self.name = name
        self.skype = None

    def connect(self):
        bus = dbus.SessionBus()
        proxy = bus.get_object('com.Skype.API', '/com/Skype')
        self.skype = dbus.Interface(proxy, 'com.Skype.API')
        self.skype.Invoke('#A NAME ' + self.name)
        self.skype.Invoke('#A PROTOCOL 8')

    def check(self):
        failure = None
        try:
            if self.skype is not None:
                try:
                    self.skype.Invoke('#A GET USERSTATUS')
                except DBusException, e:
                    if e.message.startswith('The name :'):
                        #means connection is stale and should be reacquired
                        print "Connection stale, reaquire"
                        self.skype = None
                    else:
                        raise 

            if self.skype is None:
                self.connect()
            original = self.skype.Invoke ('#A GET USERSTATUS')
            original = original[len("#A USERSTATUS "):]
            temp = 'AWAY' if original != 'AWAY' else 'INVISIBLE'
            res2 = self.skype.Invoke('#B SET USERSTATUS ' + temp)
            time.sleep(1)
            state2 = self.skype.Invoke('#D GET USERSTATUS')
            res3 = self.skype.Invoke('#C SET USERSTATUS ' + original)
            time.sleep(1)
            state3 = self.skype.Invoke('#E GET USERSTATUS')
            failure = (res2 != "#B USERSTATUS " + temp or res3 != "#C USERSTATUS " + original or 
                        state2 != '#D USERSTATUS ' + temp or state3 != '#E USERSTATUS ' + original)
        except DBusException, e:
            #no reply - failure
            print "No response from dbus"
            print e
            failure = True
     
        if failure:
            print "Check failed, restarting"
            self._restart_skype()
        else:
            print "Check OK"

    def _restart_skype(self):
        for p in psi.process.ProcessTable().values():
            if p.name.startswith('skype'):
                #kill process
                print "Killing %s %s" % (p.pid, p.name)
                self._hardly_kill(p)

        #now start new instance
        subprocess.Popen(["skype"])
        print "New instance started"

    def _hardly_kill(self, p):
        #first try to kill softly
        print "Softly killing %i" % p.pid
        p.kill(15)
        
        try:
            p = psi.process.Process(p.pid)
            print "Hardly killing %i" % p.pid
            p.kill(9)
        except ValueError, e:
            # soft kill success
            return
        

if __name__ == "__main__":
    checker = DbusChecker()
    while True:
        print "Next check executed at %i" % time.time()
        checker.check()
        time.sleep(60)

