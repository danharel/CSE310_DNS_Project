from socket import *

# Assign the ephemeral port to the server
serverPort = 0

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)

print "Server started with address %s and port %d" % serverSocket.getsockname()
print serverSocket.getsockname()

while True:
    print 'Ready to serve...'
    connectionSocket, addr = serverSocket.accept()
    data = connectionSocket.recv(1024)
    print "Received data: " + data

    if data == 'exit server':
        break

print "Exiting..."
serverSocket.close()