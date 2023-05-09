# Data provider for the F1_T00_Motion implementation
# Receives data from F1_Splitter via UDP Port 20778 and splits it and sends data to an specified UDP port for the OpenMCT server.

import socket
import time
import struct
import json

# Listens to this port from the splitter
UDP_PORT_0 = 20778   #chosen port to Motion feed

UDP_IP = "127.0.0.1" #standard ip udp (localhost)
UDP_PORT =50022   #chosen port to OpenMCT (same as in telemetry server object)
MESSAGE = "23,567,32,4356,456,132,4353467" #init message


# Connects to OpenMCT server - initiate socket and send first message
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
try:
    sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
except:
    print('Initial message failed!')

#Receiver socket from splitter
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('127.0.0.1', UDP_PORT_0))


#Still to do:
#Session offset time!
#Only unpack as we need to.
#Send one message for whole lot

count = 0

while True:

    #message, address = server_socket.recvfrom(1024000)
    message = None
    try:
        message, address = server_socket.recvfrom(1024000)
    except KeyboardInterrupt:
        print("User stopped: F1_T00_Motion.")
        exit()
    except:
        print("Timeout: F1_T00_Motion waiting for more data from port:", UDP_PORT_0) 

    if message is not None:

        # Check message is correct length, per documentation
        if len(message) != 1464:
            continue

        #print(message)
        #server_socket.sendto(message, address)
    
        #Check Header for correct message type
        #print(struct.unpack('<HBBBBqfIBB', message[0:24]))
        #print(struct.unpack('<B',message[5:6]))
    
        #if struct.unpack('<B',message[5:6])[0] == 6:
        #print(len(message))
        #lapDistanceArray = None
        #if len(message) >= 1435:
        #    #print(struct.unpack('<ffffffffffffffffffffff', message[0:88]))
        #    lapDistanceArray = struct.unpack('<ffffffffffffffffffffff', message[0:88])
        #    message = message[88:]


        if message[5:6] == b'\x00':
            #b'\x00' = 0 Motion

            #---Send the whole message at once---
            #Fake the timestamp for now, until we figure out how to offset properly
            timeStamp = time.time()

            # Unpack and send for now
            # Header
            header = struct.unpack('<HBBBBQfIBB', message[0:24])
            #print(header)
            
            # Bytes
            byteCode = '<'
            for x in range(22):
                byteCode = byteCode + 'ffffffHHHHHHffffff'
            byteCode = byteCode + 'ffffffffffffffffffffffffffffff'

            unpacked = struct.unpack(byteCode, message[24:1464])
            #print(unpacked)
            #print("Break")

            # Full message send
            #MESSAGE = "{},{},{},{}".format(header + unpacked)
            MESSAGE = "{}".format(json.dumps(["packet_00", header, unpacked, timeStamp]));
            #MESSAGE = str(header + unpacked)
            #print(MESSAGE)
            sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))

            count = count + 1
            if count % 1000 == 0:
                print("    Packet 00 messages sent: " + str(count))

