""" Executable for running doctor skype as daemon """

import logging.config
import os.path
import sys
import time

_logger = logging.getLogger()

def run(interval=60):
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
            handler.baseFilename = log_file
            break
    global _logger
    _logger = logging.getLogger(__name__)

    print "Initialized logging to %s" % os.path.abspath(log_file)
    _logger.info("Initialized logging")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Run skype watching doctorskype')
    parser.add_argument('-l', '--log-file', help='log file path, default ./doctor-skype.log', default="./doctor-skype.log")
    parser.add_argument('-n', '--interactive', help='specify to run in non-daemon mode', action='store_true')
    parser.add_argument('-i', '--interval', help='Interval in seconds how much to sleep between skype checking', default=60, type=int)

    args = parser.parse_args()

    _init_logging(args.log_file)
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

    if args.interactive:
        _logger.info("Run doctor skype in interactive mode")
        run(args.interval)
    else:
        try:
            import daemon
        except ImportError:
            _logger.exception("Failed to load python-daemon module")
            sys.stderr.write("python-daemon library should be installed\n")

        #now save all logging filehandlers
        streams = []
        for handler in logging.getLogger().handlers:
            if getattr(handler, 'stream', False):
                streams.append(handler.stream)
        with daemon.DaemonContext(files_preserve=streams):
            _logger.info("Start doctor skype in daemon mode")
            run(args.interval)

