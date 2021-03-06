from socket import *
import argparse
from sys import argv
import cmd

HOSTNAME = '127.0.0.1'
PORT = 4254 + 5000

HELP = 'HELP'
ERROR_STR = "ERROR"

NOT_CONNECTED_STR = "Not connected to a name server. Please enter the type of the server you'd like to connect to."

PUT_USAGE_STR = '    put <name> <value>\n'
GET_USAGE_STR = '    get <name>\n'
DEL_USAGE_STR = '    del <name>\n'
TYPE_USAGE_STR = '    type <type>\n'

HELP_STR = ''
HELP_STR += 'Commands:\n'
HELP_STR += '    help\n'
HELP_STR += '        Prints out this help menu.\n'
HELP_STR += TYPE_USAGE_STR
HELP_STR += '        Connects to the specified type DNS server.\n'
HELP_STR += '    done\n'
HELP_STR += '        Disconnects from the connected type DNS server.\n'
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

# Predefined status codes
PROTOCOL = "DNS/1.0"
OK = "200"
CREATED = "201"
BAD_REQUEST = "400"
NOT_FOUND = "404"
SERVICE_UNAVAILABLE = "503"

# Code that will run when the file is first executed
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
    prompt = '\n> '

    def __init__(self, hostname, portnumber):
        cmd.Cmd.__init__(self)

        print "Hello"

        self.server_type = None

        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect((hostname, portnumber))

            self.manager_sock = self.sock
        except Exception as e:
            print e
            print "Could not connect to manager. Please check hostname and port number, then try again."

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
        if not self.server_type:
            print NOT_CONNECTED_STR
            return

        parts = args.split(' ')
        if len(parts) != 2:
            print 'Invalid format'
            print PUT_USAGE_STR
        else:
            message = PROTOCOL + " PUT " + parts[0] + " " + self.server_type + " " + parts[1]
            self.sock.sendall(message)
            response, lines = self.receive_response()
            if not self.validate_response(response):
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
        if not self.server_type:
            print NOT_CONNECTED_STR
            return

        parts = args.split(' ')
        if len(parts) != 1:
            print 'Invalid format'
            print GET_USAGE_STR
        else:
            message = PROTOCOL + " GET " + parts[0] + " " + self.server_type
            self.sock.sendall(message)
            response, lines = self.receive_response()
            if not self.validate_response(response):
                return
            response_code = response[1]
            if response_code == OK:
                print "Name Type Value"
                print lines[1].strip()
            elif response_code == NOT_FOUND:
                print "Record not found."
            elif response_code == BAD_REQUEST:
                print "Invalid GET request."
            elif response_code == SERVICE_UNAVAILABLE:
                print "Server was unable to process GET. Please try again later."

    # Deletes an entry from the database
    def do_del(self, args):
        if not self.server_type:
            print NOT_CONNECTED_STR
            return

        parts = args.split(' ')
        if len(parts) != 1:
            print 'Invalid format'
            print DEL_USAGE_STR
        else:
            message = PROTOCOL + " DELETE " + parts[0] + " " + self.server_type
            self.sock.sendall(message)
            response, lines = self.receive_response()
            if not self.validate_response(response):
                return
            response_code = response[1]
            if response_code == OK:
                print "Record deleted."
            elif response_code == NOT_FOUND:
                print "Record not found."
            elif response_code == BAD_REQUEST:
                print "Invalid DELETE request."
            elif response_code == SERVICE_UNAVAILABLE:
                print "Server was unable to process DELETE. Please try again later."

    # Prints out all entries
    def do_browse(self, args):
        if not self.server_type:
            print NOT_CONNECTED_STR
            return

        message = PROTOCOL + " BROWSE"
        self.sock.sendall(message)
        response, lines = self.receive_response()
        if not self.validate_response(response):
            return
        response_code = response[1]
        if response_code == OK:
            print "Name Type Value"
            for i in xrange(1, len(lines)):
                print lines[i].strip()
        elif response_code == NOT_FOUND:
            print "Database is empty."
        elif response_code == BAD_REQUEST:
            print "Invalid BROWSE request."
        elif response_code == SERVICE_UNAVAILABLE:
            print "Server was unable to process BROWSE. Please try again later."

    # Contacts the manager for the address to the given nameserver, then connects to it
    def do_type(self, args):
        if self.server_type:
            print 'You are already connected to a name server. Type "done" if you are done with this type.'
            return

        parts = args.split(' ')
        if len(parts) != 1:
            print 'Invalid format'
            print TYPE_USAGE_STR
        else:
            server_type = parts[0]
            message = '%s TYPE %s' % (PROTOCOL, server_type,)
            self.sock.sendall(message)
            response, lines = self.receive_response()
            if not self.validate_response(response):
                return
            response_code = response[1]
            if response_code == OK:
                address = lines[1].split(' ')
                print address
                #Try to connect to the nameserver
                server_host = address[0]
                if server_host == '0.0.0.0':
                    server_host = "localhost"
                server_port = int(address[1])
                connected = self.connect_to_nameserver(server_host, server_port)
                if connected:
                    print "Connection established with %s nameserver" % (server_type)
                    self.server_type = server_type
                else:
                    print "Unable to connect to nameserver. Please try again."
            elif response_code == BAD_REQUEST:
                print "Invalid TYPE request."
            elif response_code == NOT_FOUND:
                print "Name server not found."
            elif response_code == SERVICE_UNAVAILABLE:
                print "Server was unable to process TYPE. Please try again later."

    # Closes connection with the current name server and allows the user to connect to request a new name server
    def do_done(self, args):
        if not self.server_type:
            print NOT_CONNECTED_STR
            return

        self.sock.close()
        self.sock = self.manager_sock

        print "Connection with nameserver has been closed."

        self.server_type = None

    # Exits the client
    def do_exit(self, args):
        self.manager_sock.close()
        if self.server_type:
            self.sock.close()
        return True

    # Prints out the help string if none of the above commands are entered.
    def do_default(self, args):
        print HELP_STR

    # Cleans up at the end of the loop
    def postloop(self):
        print "Exiting..."
        self.sock.close()

    # Reads from socket until the string "\r\n\r\n" is reached.
    # Returns a tuple (response, body).
    def receive_response(self):
        data = ""
        leading_whitespace = True   # Used to ignore leading whitespace
        while(not data.endswith("\r\n\r\n")):
            buffer = self.sock.recv(1024)
            if leading_whitespace:
                if buffer.strip() != "":
                    leading_whitespace = False
            if not leading_whitespace:
                data += buffer
        lines = data.split("\r\n")
        lines = lines[:len(lines) - 2] # Remove trailing blank lines
        response = lines[0].split(" ")
        body = []
        if len(lines) > 1:
            body = lines[0:]
        return (response, body)

    # Checks if the given response is valid.
    # The response is valid if it is using the DNS/1.0 protocol
    #   and contains the protocol, status code, and status phrase.
    # If the response is not valid, this funciton also prints the response
    #   and the string "Incalid response."
    def validate_response(self, response):
        if len(response) < 3 or response[0] != PROTOCOL:
            # Invalid response
            print lines
            print "Invalid response."
            return False
        else:
            return True

    # Connects to the nameserver at (host, port).
    # Returns True if successful, False otherwise
    def connect_to_nameserver(self, host, port):
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect((host, port))

            return True
        except Exception as e:
            print e
            return False

if __name__ == '__main__':
    main(argv[1:])