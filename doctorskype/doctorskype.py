import dbus
from dbus.exceptions import DBusException
import subprocess
import psi
import psi.process
import logging
import time
 
_logger = logging.getLogger(__name__)

class DbusChecker(object):

    def __init__(self, name='DoctorSkype'):
        self.name = name
        self.skype = None

    def connect(self):
        _logger.info("Establish new connection to skype dbus")
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
                        _logger.warn ("Connection stale, reaquire")
                        self.skype = None
                    else:
                        _logger.exception("Failed to check skype status")
                        raise 

            if self.skype is None:
                self.connect()
            original = self.skype.Invoke ('#A GET USERSTATUS')
            original = original[len("#A USERSTATUS "):]
            temp = 'AWAY' if original != 'AWAY' else 'INVISIBLE'
            res2 = self.skype.Invoke('#B SET USERSTATUS ' + temp)
            time.sleep(1)
            state2 = self.skype.Invoke('#D GET USERSTATUS')
            _logger.debug("Set temp status [%s], response %s, result %s", temp, res2, state2)
            res3 = self.skype.Invoke('#C SET USERSTATUS ' + original)
            time.sleep(1)
            state3 = self.skype.Invoke('#E GET USERSTATUS')
            _logger.debug("Reset original status [%s], response %s, results %s", original, res3, state3)
            failure = (res2 != "#B USERSTATUS " + temp or res3 != "#C USERSTATUS " + original or 
                        state2 != '#D USERSTATUS ' + temp or state3 != '#E USERSTATUS ' + original)
        except DBusException, e:
            #no reply - failure
            _logger.exception("No response from dbus")
            failure = True
     
        if failure:
            _logger.info("Check failed, restarting")
            self._restart_skype()
        else:
            _logger.info("Check ok")

    def _restart_skype(self):
        for p in psi.process.ProcessTable().values():
            if p.name.startswith('skype'):
                #kill process
                _logger.info("Killing %s %s", p.pid, p.name)
                self._hardly_kill(p)

        #now start new instance
        new_pid = subprocess.Popen(["skype"])
        _logger.info ("New instance started pid %s", new_pid)

    def _hardly_kill(self, p):
        #first try to kill softly
        _logger.info ("Softly killing %i", p.pid)
        p.kill(15)
        
        try:
            p = psi.process.Process(p.pid)
            _logger.info("Hardly killing %i", p.pid)
            p.kill(9)
        except ValueError, e:
            # soft kill success
            return

