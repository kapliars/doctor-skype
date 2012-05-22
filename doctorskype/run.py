#!/usr/bin/env python
""" Executable for running doctor skype as daemon """

import logging.config
import os.path
import sys
import time
import lockfile
import argparse
import pwd
import ConfigParser
 
_logger = logging.getLogger()

def run(interval=60):
    _logger.info("Started doctor skype, interval is %d sec", interval)

    from doctorskype import DbusChecker as Checker
    checker = Checker()
    try:
        while True:
            checker.check()
            time.sleep(interval)
    except:
        _logger.exception("Stopped doctor skype")

def _init_logging(log_file):
    print "Load logging config from " + os.path.dirname(__file__) + "/logging.conf"
    logging.config.fileConfig(os.path.dirname(__file__) + "/logging.conf")
    root = logging.getLogger()
    for handler in root.handlers:
        if handler.__class__ == logging.FileHandler:
            # create a new one which totally follows this
            copy = logging.FileHandler(log_file, mode=handler.mode, encoding=handler.encoding)
            copy.setFormatter(handler.formatter)
            copy.setLevel(handler.level)
            root.addHandler(copy)
            root.removeHandler(handler)
            break
    global _logger
    _logger = logging.getLogger(__name__)

    print "Initialized logging to %s" % os.path.abspath(log_file)
    _logger.info("Initialized logging")
    _logger.debug("with debug enabled")

def run_daemon(pid_file_disabled=False, pid_file_path=None, interval=60, uid=None, gid=None, working_dir=None):
    _logger.debug('Now display %s', os.environ['DISPLAY'])
    try:
        import daemon
        import daemon.pidlockfile
    except ImportError:
        _logger.exception("Failed to load python-daemon module")
        sys.stderr.write("python-daemon library should be installed\n")
        raise

    try:
        if pid_file_disabled:
            _logger.info('Start doctor skype daemon with no pidfile, uid: %s, gid: %s', uid, gid)
            pidfile = None 
        else:
            _logger.info("Start doctor skype in daemon mode, uid: %s, gid %s", uid, gid)
            pidfile = daemon.pidlockfile.TimeoutPIDLockFile(pid_file_path, 2) 

        with daemon.DaemonContext(files_preserve=_get_logging_streams(), pidfile=pidfile):
            try:
                if gid and uid:
                    os.setgid(gid)
                    os.setuid(uid)
                    if working_dir:
                        os.chdir(working_dir)
                _logger.debug('Now display %s', os.environ['DISPLAY'])
                run(interval)
            except:
                _logger.exception("Exception while running doctor skype")
                raise

    except:
        _logger.exception("Exception while running daemon")
        raise

def _get_logging_streams():
    #now save all logging filehandlers
    streams = []
    for handler in logging.getLogger().handlers:
        if getattr(handler, 'stream', False):
            streams.append(handler.stream)
    return streams

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run skype watching doctorskype')
    parser.add_argument('-P', '--no-pid-file', help='disable pid file locking', action='store_true')
    parser.add_argument('-p', '--pid-file', help='pid file path')
    parser.add_argument('-l', '--log-file', help='log file path, default ./doctor-skype.log', default="./doctor-skype.log")
    parser.add_argument('-n', '--interactive', help='specify to run in non-daemon mode', action='store_true')
    parser.add_argument('-i', '--interval', help='Interval in seconds how much to sleep between skype checking', default=60, type=int)
    parser.add_argument('-c', '--config', help='Config file path')

    args = parser.parse_args()

    _init_logging(args.log_file)

    # add path, so it can be run from anywhere
    sys.path.append(os.path.dirname(os.path.dirname(__file__))) 

    pid_file_disabled = not args.no_pid_file
    if not pid_file_disabled and args.pid_file:
        pid_file_path = args.pid_file
    else:
        pid_file_path = os.path.abspath(os.path.join(__file__, '..', '..', 'doctor_skype.pid'))

    if args.interactive:
        _logger.info("Run doctor skype in interactive mode")
        run(args.interval)
    else:
        _config = ConfigParser.SafeConfigParser()
        _config.load_file(args.config)
        user = pwd.getpwnam(_config.getstring('common', 'username'))

        run_daemon(pid_file_disabled, pid_file_path, args.interval, uid=user.pw_uid, gid=user.pw_gid)

