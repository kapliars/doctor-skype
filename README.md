Doctor Skype
===============

healing for skype linux. Monitors that skype for linux is alive and if it froze restarts process

### Installation
No automated installation (which is setup_tools) is supported yet. 

Dependencies:
- python.h. Python binding headers, on ubuntu {{sudo apt-get install python-dev}}
- setup-tools. 
- psi. Python module to manage linux process info. {{sudo easy_install psi}}
- daemon. Python module to create detached process [http://pypi.python.org/pypi/python-daemon/].{{sudo apt-get install python-daemon}}

### Running
Just go to project folder and invoke run.py:
```
cd doctor-skype
doctorskype/run.py
```

This will start doctorskype as a daemon, with logging forwarded to <project-folder>/doctor-skype.log. Check this file for errors.

## Usage
You can change logging file or run it in non-deamonized mode using command line parameters, pls invoke
```
doctorskype/run.py -h
```
to see available options

### Known issues
- since skype aliveness check is based on changing of status, this turns so automatically status (AWAY and NOT AVAILBLE)
becomes user status, and is not changed back. 

### TBD
To be done:
- detect aliveness on non meaningfull property, not status