import ip_address
from multiprocessing import Process, Queue
import os.path
from server import DNSRequestHandler, start_dns_server
import socket
import SocketServer
from ThreadedTCPServer import *
import threading

FILE_NAME = "manager.in"
server_addresses = {}

OK_STR =            "DNS/1.0 200 OK\r\n"
BAD_REQUEST_STR =   "DNS/1.0 400 Bad Request\r\n"
NOT_FOUND_STR =     "DNS/1.0 404 Not Found\r\n"

class ManagerRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        while data:
            print "Received: {}".format(data)

            bad_request = False
            parts = data.strip().split(" ")
            if len(parts) < 2:
                bad_request = True
            elif parts[0] == "DNS/1.0":
                if parts[1] == "TYPE":
                    if len(parts) < 3:
                        bad_request = True
                    else:
                        type = parts[2].upper()
                        if type in server_addresses:
                            address = server_addresses[type]
                            self.request.sendall(OK_STR)
                            self.request.sendall("{} {}\r\n".format(address[0], address[1]))
                        else:
                            self.request.sendall(NOT_FOUND_STR)
                else:
                    bad_request = True
            else:
                bad_request = True
            if bad_request:
                self.request.sendall(BAD_REQUEST_STR)
            self.request.sendall("\r\n")
            data = self.request.recv(1024)

def start_dns_server_process(address_queue, type):
    address = start_dns_server("{}.txt".format(type))
    print "{} DNS Server started at {}:{}".format(type, address[0], address[1])
    address_queue.put(address)

def main():
    address_queue = Queue()
    success = False
    try:
        with open(FILE_NAME, "r") as file:
            for line in file:
                type = line.strip().upper()
                if type != "" not in server_addresses: # Ignore repeat types
                    #p = Process(target=start_dns_server_process, args=(address_queue,type,))
                    p = threading.Thread(target=start_dns_server_process, args=(address_queue,type,))
                    p.start()
                    address = address_queue.get()
                    server_addresses[type] = address
            success = True
    except IOError:
        print "Unable to read " + FILE_NAME

    if success:
        # Assign the ephemeral port to the server
        HOST, PORT = ip_address.get(), 4254

        server = ThreadedTCPServer((HOST, PORT), ManagerRequestHandler)

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.start()

        print "DNS Manager Server started with address %s and port %d" % server.server_address
        print "Ready to serve..."
    else:
        print "DNS Manager Server not started"

if __name__ == '__main__':
    main()