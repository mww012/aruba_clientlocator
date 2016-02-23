# Aruba AP Finder

This script is intended to help the user find APs as well as help troubleshoot client roaming.

This python script will do at least one of the following for a given sta:
* Notify user of the current associated AP via the Pushover notification service
* Blink the lights on the currently associated AP

This script ssh's into the master controller, runs ```show global-user-table list mac-addr <mac>``` and parses the response.  This script will run indefinitely until killed by the user.  Because of the way Paramiko handles ssh, each command will spin up a ssh session every time a command is sent(Not great, I know, but it works.  See to-do's).

*NOTE: When the script process is killed, if an AP was blinking it will not be set back to normal.  This must be done manually.* 

Usage: ```aruba_apfinder.py <options>``` <br />
 ```aruba_apfinder.py -m <ip> -e <enable password> -u <username> -p <password> -b -p -pt <app token> -pk <user key>```

| Option | Description | Required | 
|--------|-------------|----------|
|-m, --master|Master Controller IP Address|Yes|
|-e, --enable|Controller's enable password|Yes|
|-u, --user|SSH Username|Yes|
|-pw, --password|SSH Password|Yes|
|-b --blink|Blink APs|No|
|-p --pushover|Send Pushover Notifications|No|
|-pt, --pushtoken|Pushover Application Token|Yes, if -p is set|
|-pk, --pushkey|Pushover User Key|Yes, if -p is set|


## Requirements:
* Pushover 
  * A valid Pushover account(https://pushover.net) is required for sending notifications(yes, it's free).
  * An application in Pushover must be created(I recommend a dedicated application).

* Python Modules:
  * Netaddr
  * Paramiko
  * All others should be built-in

## TO-DO:
- [ ] Write the AP associations a times to a log file
- [ ] Optimize SSH sessions so that a single SSH tunnel is established and kept open for the life of the script.
- [ ] Handle SIGINT so that the script cleans up any running commands instead of just quitting.
