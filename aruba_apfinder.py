"""
This script is intended to be used in an Aruba Networks wireless environment.
"""

import argparse
import netaddr
import sys
import multiprocessing
import aruba_ssh


def ipv4(string):
    return str(netaddr.IPAddress(string))


def mac_addr(string):
    return str(netaddr.EUI(string))

def main():
    parser = argparse.ArgumentParser(description=(
        'This script will do at least one'
        ' of the following for a given sta:\n'
        '- Notify user of the current associated AP via the Pushover '
        'notification service\n'
        '- Blink the lights on the currently associated AP\n'
        '- Write the AP associations a times to a log file'),
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-m', '--master', required=True, metavar="IP",
                        type=ipv4, help="Master Controller IP Address")
    parser.add_argument('-e', '--enable', required=True, metavar="ENABLEPW",
                        help='Controller enable password')
    parser.add_argument('-t', '--targetsta', required=True, metavar="STAMAC",
                        type=mac_addr,
                        help="Station mac address you want to target")
    parser.add_argument('-u', '--user', required=True, type=str,
                        help="SSH Username")
    parser.add_argument('-pw', '--password', required=True,
                        help="SSH Password")
    parser.add_argument('-b', '--blink',action='store_true',
                        help="Blink currently associated AP")
    parser.add_argument('-l', '--log', type=argparse.FileType('w'),
                        help='Logs station associations and timestamps to a '
                             'given file')
    pushover = parser.add_argument_group('Pushover Notifications',
                                         'Configuration to send push '
                                         'notifications to the Pushover '
                                         'service')
    pushover.add_argument('-p', '--pushover',
                          help="Utilize Pushover service for current AP "
                               "notification")
    pushover.add_argument('-pt', '--pushtoken', metavar="TOKEN",
                          help="Pushover Application Token")
    pushover.add_argument('-pk', '--pushkey', metavar="KEY",
                          help="Pushover User Key")

    arguments = parser.parse_args()
    print arguments
    # controllers = aruba_ssh.enum_controllers(arguments.master,
    #                                          arguments.user,
    #                                          arguments.password,
    #                                          arguments.enable)
    controllers=['10.1.200.242']

    queues = {}
    for controller in controllers:
        queues[controller] = multiprocessing.Queue()
        ssh_session = multiprocessing.Process(target=aruba_ssh.ssh_session,
                                              args=(controller,
                                                    arguments.user,
                                                    arguments.password,
                                                    arguments.enable,
                                                    queues[controller]),
                                              name=str(controller))
        ssh_session.start()
    queues[controllers[0]].put('show ap database\n')


    for queue in queues:
        queues[queue].put('close')


if __name__ == "__main__":
    sys.exit(main())


