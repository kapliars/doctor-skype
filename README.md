Doctor Skype
===============

healing for skype linux. Monitors that skype for linux is alive and if it froze restarts process

### Installation
No automated installation (which is setup_tools) is supported yet. You'll need [daemon module|http://pypi.python.org/pypi/python-daemon/] installed. On ubuntu invoke {{sudo apt-get install python-daemon}}.

### Running
Just go to project folder and invoke run.py:
```
cd doctor-skype
doctorskype/run.py
```

## Usage
You can change logging file or run it in non-deamonized mode using command line parameters, pls invoke
```
doctorskype/run.py -h
```
for details

### Known issues
- since skype aliveness check is based on changing of status, this turns so automatically status (AWAY and NOT AVAILBLE)
becomes user status, and is not changed back. 

### TBD
To be done:
- detect aliveness on non meaningfull property, not status
