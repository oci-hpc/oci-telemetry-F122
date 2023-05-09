# Data provider for the F1_T05_Car_Setups implementation
# Receives data from F1_Splitter via UDP Port 20783 and splits it and sends data to an specified UDP port for the OpenMCT server.

import socket
import time
import struct
import json

# Listens to this port from the splitter
UDP_PORT_0 = 20783   #chosen port to Car Setups feed

UDP_IP = "127.0.0.1" #standard ip udp (localhost)
UDP_PORT =55022   #chosen port to OpenMCT (same as in telemetry server object)
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


count = 0

while True:

    #message, address = server_socket.recvfrom(1024000)
    message = None
    try:
        message, address = server_socket.recvfrom(1024000)
    except KeyboardInterrupt:
        print("User stopped: F1_T05_Car_Setups.")
        exit()
    except:
        print("Timeout: F1_T05_Car_Setups waiting for more data from port:", UDP_PORT_0) 

    if message is not None:

        # Check message is correct length, per documentation
        if len(message) != 1102:
            continue

        #print(message)
        #server_socket.sendto(message, address)
        
        #Check Header for correct message type
        #print(struct.unpack('<HBBBBQfIBB', message[0:24]))
        #print(struct.unpack('<B',message[5:6]))
        
        
        if message[5:6] == b'\x05':
            #b'\x05' = 5 Car Setups

            #---Send the whole message at once---
            timeStamp = time.time()

            # Unpack and send for now
            # Header
            header = struct.unpack('<HBBBBQfIBB', message[0:24])
            #print(header)
            
            # Bytes
            byteCode = '<'
            for x in range(22):
                byteCode = byteCode + 'BBBBffffBBBBBBBBffffBf'
            #byteCode = byteCode + 'ffffffffffffffffffffffffffffff'

            unpacked = struct.unpack(byteCode, message[24:1102])
            
            #print(unpacked)
            #print("Break")


            # Full message send
            #MESSAGE = "{},{},{},{}".format(header + unpacked)
            MESSAGE = "{}".format(json.dumps(["packet_05", header, unpacked, timeStamp]));
            #MESSAGE = str(header + unpacked)
            #print(MESSAGE)
            sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))

            count = count + 1
            if count % 1000 == 0:
                print("    Packet 05 messages sent: " + str(count))
