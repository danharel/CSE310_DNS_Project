import threading
import SocketServer

server = None

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024);
        print "Received data: {}".format(data)
        if data == 'exit server':
            print "Exiting..."
            server.shutdown()
            server.server_close()

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