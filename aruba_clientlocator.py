"""
This script is intended to be used in an Aruba Networks wireless environment.
"""

import argparse
import netaddr
import sys
import re
import time
import aruba_device
import pushover

def ipv4(string):
    return str(netaddr.IPAddress(string))


def mac_addr(string):
    mac = netaddr.EUI(string)
    mac.dialect = netaddr.mac_unix_expanded
    return str(mac)


def main():
    # Set up parser for script arguments
    parser = argparse.ArgumentParser(description=(
        'This script will do at least one'
        ' of the following for a given sta:\n'
        '- Notify user of the current associated AP via the Pushover '
        'notification service\n'
        '- Blink the lights on the currently associated AP\n'
        '- Write the AP associations and times to a log file'),
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-m',
                        '--master',
                        required=True,
                        metavar="IP",
                        type=ipv4,
                        help="Master Controller IP Address")
    parser.add_argument('-e',
                        '--enable',
                        required=True,
                        metavar="ENABLEPW",
                        help='Controller enable password')
    parser.add_argument('-t',
                        '--targetsta',
                        required=True,
                        metavar="STAMAC",
                        type=mac_addr,
                        help="Station mac address you want to target")
    parser.add_argument('-u',
                        '--user',
                        required=True,
                        type=str,
                        help="SSH Username")
    parser.add_argument('-pw',
                        '--password',
                        required=True,
                        help="SSH Password")
    parser.add_argument('-b',
                        '--blink',
                        action='store_true',
                        help="Blink currently associated AP")
    parser.add_argument('-l',
                        '--log',
                        type=argparse.FileType('w'),
                        help='Logs station associations and timestamps to a given file')

    pushover_args = parser.add_argument_group('Pushover Notifications',
                                         'Configuration to send push notifications to the Pushover service')
    pushover_args.add_argument('-p',
                          '--pushover',
                          action='store_true',
                          help="Utilize Pushover service for current AP notification")
    pushover_args.add_argument('-pt',
                          '--pushtoken',
                          metavar="TOKEN",
                          help="Pushover Application Token")
    pushover_args.add_argument('-pk',
                          '--pushkey',
                          metavar="KEY",
                          help="Pushover User Key")

    # Parse argumnets in the "arguments" array
    arguments = parser.parse_args()
    # If pushover argument exists, the appkey and usertoken must exist.
    if arguments.pushover:
        if (arguments.pushtoken is None or arguments.pushkey is None):
            parser.error('-p/--pushover requires -pt/--pushtoken and -pk/--pushkey')
        push = pushover.pushover_connection(arguments.pushtoken,arguments.pushkey)
        
    # Create master controller object
    master = aruba_device.controller(arguments.master,
                                     arguments.user,
                                     arguments.password,
                                     arguments.enable)

    # Regex to pull needed info from "show global-user-table list mac-addr <mac> command.
    # Capturing all fields for potential future use
    user_regex = re.compile('(?P<userip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*'
                            '(?P<usermac>[A-Fa-f0-9\:]{17})\s*'
                            '(?P<username>.*?)\s*'
                            '(?P<controllerip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*'
                            '(?P<userrole>\w*)\s*'
                            '(?P<userage>[\d\:]*)\s*'
                            '(?P<authmode>[\w\.]*)\s*'
                            '(?P<apname>[\w\-]*)\s*'
                            '(?P<connectiontype>[\w]*)\s*'
                            '(?P<essid>[\w-]*)\s*'
                            '(?P<bssid>[A-Fa-f0-9\:]{17})\s*'
                            '(?P<connectionmode>[\w\-]*)\s*'
                            '(?P<aaaprofile>[\w\-]*)\s*'
                            '(?P<devtype>[\w]*)')
    
    current_loc = {'ap': '',
                'online': '',
                'controller': ''}
    
    # Loop until process is killed
    while True:
        # Send command to find user.  Command must be sent twice on the master controller to get good info.
        result = master.send_cmd(
            ['show global-user-table list mac-addr ' + arguments.targetsta])
        if 'The master controller is collecting information from local controllers. Please check the results later.' in result:
            result = master.send_cmd(['show global-user-table list mac-addr ' + arguments.targetsta])
        # Parse command results.  If command fails, output will be None.
        output = user_regex.search(result)
        if output is not None:
            # Found user
            current_loc['online'] = True
            # Compare latest ap and take action based on given switches
            if current_loc['ap'] != output.group('apname'):
                if arguments.blink:
                    master.send_cmd(['ap-leds ap-name ' + current_loc['ap'] + ' normal'])
                    master.send_cmd(['ap-leds ap-name ' + output.group('apname') + ' blink'])
                if arguments.pushover:
                    push.send_message('New: ' +
                                      output.group('apname') +
                                      '\n' +
                                      'Controller: ' +
                                      output.group('controllerip'))
                current_loc['ap'] = output.group('apname')
                current_loc['controller'] = output.group('controllerip')
        elif output is None:
            # No user found.  User not in user table on master controller.
            if current_loc['online'] is not False:
                push.send_message('Client not found...')
                # Ensure that last AP led status get set back to normal
                if current_loc['ap'] != '':
                    master.send_cmd(['ap-leds ap-name ' + current_loc['ap'] + ' normal'])
            print 'Client not found...'
            current_loc['online'] = False
        time.sleep(1)


if __name__ == "__main__":
    sys.exit(main())
