import threading
import SocketServer

server = None

# Handles each socket on a new thread
class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        while data:
            print "Received data: {}".format(data)

            badRequest = False

            parts = data.split(" ")
            if len(parts) <= 1:
                badRequest = True
            elif parts[0] == "DNS/1.0":
                if parts[1] == "DELETE":
                    print "Delete"
                elif parts[1] == "PUT":
                    print "Put"
                elif parts[1] == "GET":
                    print "Get"
                elif parts[1] == "BROWSE":
                    print "Browse"
                else:
                    badRequest = True
            else:
                badRequest = True
            if badRequest:
                print "Bad Request"
                # TODO
            data = self.request.recv(1024)
        # Client has closed the socket

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

def main():
    # Assign the ephemeral port to the server
    HOST, PORT = '', 0

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()

    print "Server started with address %s and port %d" % server.server_address
    print "Ready to serve..."

if __name__ == '__main__':
    main()