import socket

machineIsUnix = False
try:
    import fcntl
    import struct
    machineIsUnix = True
except:
    machineIsUnix = False

# Gets the external IP address of the machine.
# If the machine is not UNIX, a socket will be opened to
# Google's DNS server (8.8.8.8) in order to retrieve
# the machine's ip address
def get():
    if machineIsUnix:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', "eth0"[:15])
        )[20:24])
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google DNS server
        ip = s.getsockname()[0]
        s.close()
        return ip