from socket import *
import argparse
from sys import argv
import cmd

HELP = 'HELP'
ERROR_STR = "ERROR"

PUT_USAGE_STR = '    put <name> <value> <type>\n'
GET_USAGE_STR = '    get <name> <type>\n'
DEL_USAGE_STR = '    del <name> <type>\n'

HELP_STR = ''
HELP_STR += 'Commands:\n'
HELP_STR += '    help\n'
HELP_STR += '        Prints out this help menu.\n'
HELP_STR += PUT_USAGE_STR
HELP_STR += '        Adds a new name record to the database.\n'
HELP_STR += '        If the name record is already in the database, the value will be replaced with the new value.\n'
HELP_STR += GET_USAGE_STR
HELP_STR += '        Looks up and prints out the value of the record with the given name and type, or "not found" if it does not exist.\n'
HELP_STR += DEL_USAGE_STR
HELP_STR += '        Removes the record with the given name and type. Prints out a success message if it can be found, or "not found" if it does not exist.\n'
HELP_STR += '    browse\n'
HELP_STR += '        Prints out all records in the database or "database is empty" if none can be found.\n'
HELP_STR += '    exit\n'
HELP_STR += '        Exits this program.\n'


def main(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'hostname',
        help='Name of the host where the DNS server is running.'
        )

    parser.add_argument(
        'portnumber',
        type=int,
        help='Port number on which the DNS server is listening.'
        )

    args = parser.parse_args(argv)

    DNSClient(args.hostname, args.portnumber).cmdloop()

    #sock = socket(AF_INET, SOCK_DGRAM)

    # while True:
    #     usr_input = raw_input("Please enter a command: ")

    #     command = process_input(usr_input, sock)

    #     #sock.sendto(command, (args.hostname, args.portnumber))

    #     if command == 'exit client':
    #         break

class DNSClient(cmd.Cmd):
    intro = 'Please enter a command, or help for usage instructions.'
    prompt = '> '

    def __init__(self, hostname, portnumber):
        cmd.Cmd.__init__(self)

        print "Hello"

        self.hostname = hostname
        self.portnumber = portnumber
        self.sock = socket(AF_INET, SOCK_DGRAM)

        print "Done making socket"

    def precmd(self, line):
        return line.strip().lower()

    def do_help(self, args):
        print HELP_STR

    def do_put(self, args):
        parts = args.split(' ')
        if len(parts) != 3:
            print 'Invalid format'
            print PUT_USAGE_STR
        else:
            print "Putting"

    def do_get(self, args):
        parts = args.split(' ')
        if len(parts) != 2:
            print 'Invalid format'
            print GET_USAGE_STR
        else:
            print "Getting"

    def do_del(self, args):
        parts = args.split(' ')
        if len(parts) != 2:
            print 'Invalid format'
            print "Deleting"
        else:
            print "Deleting"

    def do_browse(self, args):
        print "Browsing"

    def do_exit(self, args):
        return True

    def do_default(self, args):
        print HELP_STR

    def postloop(self):
        print "Exiting..."
        self.sock.close()

if __name__ == '__main__':
    main(argv[1:])