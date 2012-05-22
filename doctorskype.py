#!/usr/bin/env python

# This is a start-stop service script for doctor skype daemon

import sys
import subprocess
import os
import time
import ConfigParser
import pwd


PIDFILE = '/var/run/doctor-skype/doctorskype.pid'
LOGFILE = '/var/log/doctor-skype/doctor-skype.log'
CONFIG_FILE='/etc/doctorskype.conf'

def _usage():
    print "Usage: doctorskype.py start|stop|restart|status"
    sys.exit(2)

def verify_access(fun):
    def _test_access(fpath):
        if os.path.exists(fpath):
            return os.access(fpath, os.R_OK | os.W_OK)
        else:
            #check we have execute and write permission to directory
            parent = os.path.dirname(fpath)
            return os.access(parent, os.R_OK | os.W_OK | os.X_OK)

    def wrapper(*args, **kwargs):
        if _test_access(PIDFILE) and _test_access(LOGFILE):
            fun(*args, **kwargs)
        else:
            print "No access to pid or log file. Normally should be run as root"
            sys.exit(3)

    return wrapper

def load_config(path):
    config = ConfigParser.SafeConfigParser()
    config.read(path)
    return config

def get_uid(username):
    user = pwd.getpwnam(username)
    return user.pw_uid, user.pw_gid, os.path.join(user.pw_dir, ".doctor_skype")

@verify_access
def _start():
    try:
        doctorskype.run._init_logging(LOGFILE)
        config = load_config(CONFIG_FILE)
        uid, gid, wd = get_uid(config.get('common', 'username'))
        doctorskype.run.run_daemon(pid_file_path=PIDFILE, interval=60, uid=uid, gid=gid, working_dir=wd) 
        print "Doctor skype started"
    except:
        print "exception!!!"
        print sys.exc_info()

@verify_access
def _stop(exit_if_not_running=True):
    if not os.path.exists(PIDFILE):
        print "Doctor skype is not running"
        if exit_if_not_running:
            sys.exit(1)
    else:
        pid = open(PIDFILE).read().strip()
        subprocess.call(['kill', pid])
        print "Doctor skype killed"

def _status():
    if not os.path.exists(PIDFILE):
        print "Doctor skype is not running, no pid file"
        return
    pid = open(PIDFILE).read().strip()
    status_file = os.path.join('/proc', pid, 'status')
    if not os.path.exists(status_file):
        print "Doctor skype is not running, no such process " + status_file
        return

    print "Doctor skype is running"

@verify_access
def _restart():
    _stop(False)
    time.sleep(2)
    _start()

if __name__ == "__main__":
    try:
        import doctorskype
        import doctorskype.run
    except ImportError as e:
        sys.stderr.write("Please install doctorskype first\n")
        sys.stderr.write(e)

    if len(sys.argv) < 2:
        _usage()

    action = sys.argv[1]

    if action == 'start':
        _start()
    elif action == 'stop':
        _stop()
    elif action == 'restart':
        _restart()
    elif action == 'status':
        _status()
    else:
        _usage()


