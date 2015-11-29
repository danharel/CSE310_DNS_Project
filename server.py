import os.path
import SocketServer
import threading

FILE_NAME = "records.txt"
lock = threading.RLock()

OK_STR = "DNS/1.0 200 OK\r\n"
CREATED_STR = "DNS/1.0 201 Created\r\n"
BAD_REQUEST_STR = "DNS/1.0 400 Bad Request\r\n"
NOT_FOUND_STR = "DNS/1.0 404 Not Found\r\n"
SERVICE_UNAVAILABLE_STR = "DNS/1.0 503 Service Unavailable\r\n"

ERROR_STR = "ERR"

# Handles each socket on a new thread
class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    # Handle the TCP request
    def handle(self):
        data = self.request.recv(1024)
        while data:
            print "Received data: {}".format(data)

            bad_request = False

            parts = data.strip().split(" ")
            # Valid requests are in the following format:
            #     DNS/1.0 METHOD name type value
            if len(parts) <= 1:
                bad_request = True
            elif parts[0] == "DNS/1.0":
                if parts[1] == "DELETE":
                    if len(parts) <= 3:
                        self.request.sendall(BAD_REQUEST_STR)
                    else:
                        lock.acquire()  # Prevent simultaneous access to records file.
                        if os.path.isfile(FILE_NAME):
                            try:
                                with open(FILE_NAME, "r+") as file:
                                    matching, unmatching = self.filter_file(file, parts[2], parts[3])
                                    if len(matching) > 0:
                                        # Rewrite the file without the matching records
                                        file.seek(0)
                                        for i in xrange(0, len(unmatching)):
                                            file.write(unmatching[i])
                                        file.truncate()
                                        self.request.sendall(OK_STR)
                                    else:
                                        self.request.sendall(NOT_FOUND_STR)
                            except IOError:
                                # Unable to open file
                                self.request.sendall(SERVICE_UNAVAILABLE_STR)
                        else:
                            self.request.sendall(NOT_FOUND_STR)
                        lock.release()

                elif parts[1] == "PUT":
                    if len(parts) <= 4:
                        self.request.sendall(BAD_REQUEST_STR)
                    else:
                        lock.acquire()  # Prevent simultaneous access to records file.
                        if os.path.isfile(FILE_NAME):
                            try:
                                with open(FILE_NAME, "r+") as file:
                                    matching, unmatching = self.filter_file(file, parts[2], parts[3])
                                    if len(matching) > 0:
                                        # If the record already exists, remove it first:
                                        file.seek(0)
                                        for i in xrange(0, len(unmatching)):
                                            file.write(unmatching[i])
                                    file.write(parts[2] + " " + parts[3] + " " + parts[4] + "\r\n")
                                    file.truncate()
                                self.request.sendall(CREATED_STR)
                            except IOError:
                                # Unable to open file
                                self.request.sendall(SERVICE_UNAVAILABLE_STR)
                        else:
                            # File does not exist, make a new one:
                            try:
                                with open(FILE_NAME, "w") as file:
                                    file.write(parts[2] + " " + parts[3] + " " + parts[4] + "\r\n")
                                    file.truncate()
                                self.request.sendall(CREATED_STR)
                            except IOError:
                                # Unable to create file
                                self.request.sendall(SERVICE_UNAVAILABLE_STR)
                        lock.release()

                elif parts[1] == "GET":
                    if len(parts) <= 3:
                        self.request.sendall(BAD_REQUEST_STR)
                    else:
                        lock.acquire()  # Prevent simultaneous access to records file.
                        if os.path.isfile(FILE_NAME):
                            try:
                                matching, unmatching = None, None
                                with open(FILE_NAME, "r") as file:
                                    matching, unmatching = self.filter_file(file, parts[2], parts[3])
                                if len(matching) == 0:
                                    self.request.sendall(NOT_FOUND_STR)
                                else:
                                    self.request.sendall(OK_STR)
                                    self.request.sendall(matching[0])
                            except IOError:
                                # Unable to open file
                                self.request.sendall(SERVICE_UNAVAILABLE_STR)
                        else:
                            self.request.sendall(OK_STR)
                        lock.release()

                elif parts[1] == "BROWSE":
                    lock.acquire()  # Prevent simultaneous access to records file.
                    if os.path.isfile(FILE_NAME):
                        try:
                            matching, unmatching = None, None
                            with open(FILE_NAME, "r") as file:
                                matching, unmatching = self.filter_file(file)
                            self.request.sendall(OK_STR)
                            for i in xrange(0, len(matching)):
                                self.request.sendall(matching[i])
                        except IOError:
                            # Unable to open file
                            self.request.sendall(SERVICE_UNAVAILABLE_STR)
                    else:
                        self.request.sendall(OK_STR)
                    lock.release()

                else:
                    self.request.sendall(BAD_REQUEST_STR)
            else:
                self.request.sendall(BAD_REQUEST_STR)
            self.request.sendall("\r\n") # Designates end of response

            data = self.request.recv(1024)
        # Client has closed the socket

    # Reads the record file line by line and returns the tuple (matching, unmatching)
    #   where matching is an array of record strings that match the filter and
    #   unmatching is an array of record strings that do not match the filter.
    # If no filter is given, then all record strings will be placed into matching
    #   and unmatching will by empty.
    def filter_file(self, file, filter_name=None, filter_type=None):
        matching = []
        unmatching = []
        for line in file:
            record = line.rstrip("\r\n").split(" ")
            if len(record) == 3:
                # Return only valid records.
                match = True
                if filter_name and record[0] != filter_name:
                    match = False
                if filter_type and record[1] != filter_type:
                    match = False

                if match:
                    matching.append(line)
                else:
                    unmatching.append(line)
        return (matching, unmatching)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

def main():
    # Assign the ephemeral port to the server
    HOST, PORT = '', 0

    print type(lock)
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()

    print "Server started with address %s and port %d" % server.server_address
    print "Ready to serve..."

if __name__ == '__main__':
    main()