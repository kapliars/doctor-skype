Doctor Skype
===============

healing for skype linux. Monitors that skype for linux is alive and if it froze restarts process

There's no deamonization at the moment, so to run just invoke
```
python doctor-skype
```
or 
```
nohup python doctor-skype > ~/log/doctor-skype.log &2>1 &
```

As you see logging is based on stdout too.

### Known issues
- since skype aliveness check is based on changing of status, this turns so automatically status (AWAY and NOT AVAILBLE)
becomes user status, and is not changed back. 

### TBD
To be done:
- add daemonization
- add logging
- detect aliveness on non meaningfull property, not status