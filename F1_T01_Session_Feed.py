# Data provider for the F1_T01_Session implementation
# Receives data from F1_Splitter via UDP Port 20779 and splits it and sends data to an specified UDP port for the OpenMCT server.

import socket
import time
import struct
import json

# Listens to this port from the splitter
UDP_PORT_0 = 20779   #chosen port to Session feed

UDP_IP = "127.0.0.1" #standard ip udp (localhost)
UDP_PORT =51022   #chosen port to OpenMCT (same as in telemetry server object)
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
        print("User stopped: F1_T01_Session.")
        exit()
    except:
        print("Timeout: F1_T01_Session waiting for more data from port:", UDP_PORT_0) 

    if message is not None:

        #print(message)

        # Check message is correct length, per documentation
        if len(message) != 632:
            continue

        #print(message)
        #server_socket.sendto(message, address)
        
        #Check Header for correct message type
        #print(struct.unpack('<HBBBBqfIBB', message[0:24]))
        #print(struct.unpack('<B',message[5:6]))
        
        
        if message[5:6] == b'\x01':
            #b'\x01' = 1 Session
            #if struct.unpack('<B',message[5:6])[0] == 1:
            
            #---Send the whole message at once---
            timeStamp = time.time()

            # Unpack and send for now
            # Header
            header = struct.unpack('<HBBBBQfIBB', message[0:24])
            #print(header)

            packet_part_1 = struct.unpack('<BbbBHBbBHHBBBBBB', message[24:43])
            #print(packet_part_1)

            packetMarshal = struct.unpack('<fbfbfbfbfbfbfbfbfbfbfbfbfbfbfbfbfbfbfbfbfb', message[43:148])
            #print(packetMarshal)

            packet_part_2 = struct.unpack('<BBB', message[148:151])

            weatherForecastBitString = '<'
            for forecast in range(56): # -1?
                weatherForecastBitString = weatherForecastBitString + 'BBBbbbbB'
            
            #print(weatherForecastBitString)
            weatherPacket = struct.unpack(weatherForecastBitString, message[151:599])
            #print(weatherPacket)
            packet_part_3 = struct.unpack('<BBIIIBBBBBBBBBBBBBBIB', message[599:632])
            #print(packet_part_3)

            unpacked = packet_part_1 + packetMarshal + packet_part_2 + weatherPacket + packet_part_3

            #print(unpacked)
            #print("Break")

            # Full message send
            #MESSAGE = "{},{},{},{}".format(header + unpacked)
            MESSAGE = "{}".format(json.dumps(["packet_01", header, unpacked, timeStamp]));
            #MESSAGE = str(header + unpacked)
            #print(MESSAGE)
            sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
            
            count = count + 1
            if count % 1000 == 0:
                print("    Packet 01 messages sent: " + str(count))
        
        
   

        
        

        

        

        

        

        

        

        