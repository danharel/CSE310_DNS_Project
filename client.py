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

PROTOCOL = "DNS/1.0"
OK = "200"
CREATED = "201"
BAD_REQUEST = "400"
NOT_FOUND = "404"
SERVICE_UNAVAILABLE = "503"

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

# Class that handles command line interfacing with the program
class DNSClient(cmd.Cmd):
    # Introductory message
    intro = 'Please enter a command, or help for usage instructions.'
    # Prompt that appears before every input
    prompt = '> '

    def __init__(self, hostname, portnumber):
        cmd.Cmd.__init__(self)

        print "Hello"

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((hostname, portnumber))

        self.sock.sendall("Hello")

        print "Done making socket"

    # Runs before every command is processed.
    # Strips the whitespace off the ends of the string, then makes it lowercase
    def precmd(self, line):
        return line.strip().lower()

    # Prints help string
    def do_help(self, args):
        print HELP_STR

    # Puts an entry into the database
    def do_put(self, args):
        parts = args.split(' ')
        if len(parts) != 3:
            print 'Invalid format'
            print PUT_USAGE_STR
        else:
            message = PROTOCOL + " PUT " + parts[0] + " " + parts[1] + " " + parts[2]
            self.sock.sendall(message)
            lines = self.receive_data()
            response = lines[0].split(" ")
            if len(response) < 3 or response[0] != PROTOCOL:
                # Invalid response
                print "Invalid response."
                return
            response_code = response[1]
            if response_code == CREATED:
                print "PUT successful."
            elif response_code == BAD_REQUEST:
                print "Invalid PUT request."
            elif response_code == SERVICE_UNAVAILABLE:
                print "Server was unable to process PUT. Please try again later."

    # Gets an entry from the database
    def do_get(self, args):
        parts = args.split(' ')
        if len(parts) != 2:
            print 'Invalid format'
            print GET_USAGE_STR
        else:
            message = PROTOCOL + " GET " + parts[0] + " " + parts[1]
            self.sock.sendall(message)
            lines = self.receive_data()
            response = lines[0].split(" ")
            if len(response) < 3 or response[0] != PROTOCOL:
                # Invalid response
                print "Invalid response."
                return
            response_code = response[1]
            if response_code == OK:
                print lines[1].strip()
            elif response_code == NOT_FOUND:
                print "Record not found."
            elif response_code == BAD_REQUEST:
                print "Invalid GET request."
            elif response_code == SERVICE_UNAVAILABLE:
                print "Server was unable to process GET. Please try again later."

    # Deletes an entry from the database
    def do_del(self, args):
        parts = args.split(' ')
        if len(parts) != 2:
            print 'Invalid format'
            print "Deleting"
        else:
            message = PROTOCOL + " DELETE " + parts[0] + " " + parts[1]
            self.sock.sendall(message)
            # TODO receive response
            print "Deleting"

    # Prints out all entries
    def do_browse(self, args):
        message = PROTOCOL + " BROWSE"
        self.sock.sendall(message)
        lines = self.receive_data()
        response = lines[0].split(" ")
        if len(response) < 3 or response[0] != PROTOCOL:
            # Invalid response
            print lines
            print "Invalid response."
            return
        response_code = response[1]
        if response_code == OK:
            for i in range(1, len(response)):
                print lines[i].strip()
        elif response_code == BAD_REQUEST:
            print "Invalid BROWSE request."
        elif response_code == SERVICE_UNAVAILABLE:
            print "Server was unable to process BROWSE. Please try again later."

    # Exits the client
    def do_exit(self, args):
        return True

    # Prints out the help string if none of the above commands are entered
    def do_default(self, args):
        print HELP_STR

    # Cleans up at the end of the loop
    def postloop(self):
        print "Exiting..."
        self.sock.close()

    def receive_data(self):
        data = ""
        buffer = self.sock.recv(1024)
        while(buffer):
            if buffer != "":
                data += buffer
            if data.endswith("\r\n\r\n"):
                break
            buffer = self.sock.recv(1024)
        return data.split("\r\n")

if __name__ == '__main__':
    main(argv[1:])