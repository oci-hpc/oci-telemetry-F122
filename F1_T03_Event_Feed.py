# Data provider for the F1_T03_Event implementation
# Receives data from F1_Splitter via UDP Port 20781 and splits it and sends data to an specified UDP port for the OpenMCT server.

import socket
import time
import struct
import json
import math

# Listens to this port from the splitter
UDP_PORT_0 = 20781   #chosen port to Event feed

UDP_IP = "127.0.0.1" #standard ip udp (localhost)
UDP_PORT =53022   #chosen port to OpenMCT (same as in telemetry server object)
MESSAGE = "23,567,32,4356,456,132,4353467" #init message

data = 0 #artificial data


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
        print("User stopped: F1_T03_Event.")
        exit()
    except:
        print("Timeout: F1_T03_Event waiting for more data from port:", UDP_PORT_0) 

    if message is not None:

        # Check message is correct length, per documentation
        if len(message) != 40:
            #exit()
            continue

        #print(message)
        #server_socket.sendto(message, address)
        
        #Check Header for correct message type
        #print(struct.unpack('<HBBBBqfIBB', message[0:24]))
        #print(struct.unpack('<B',message[5:6]))
        
        
        if message[5:6] == b'\x03':
            #b'\x03' = 3 Event
            
            #---Send the whole message at once---
            timeStamp = time.time()

            # Unpack and send for now
            # Header
            header = struct.unpack('<HBBBBQfIBB', message[0:24])
            #print(header)
            code = message[24:28].decode('utf8', 'strict')
            
            #print(code, message[28:])

            # Bytes
            byteCode = '<'
            endBit = None
            unpacked = None

            if code == "BUTN":
                # Do we even bother with button presses? I guess we could
                byteCode = byteCode + 'L'
                endBit = 32
            elif code == "SSTA":
                pass
            elif code == "SEND":
                pass
            elif code == "FTLP":
                byteCode = byteCode + 'Bf'
                endBit = 33
            elif code == "RTMT":
                byteCode = byteCode + 'B'
                endBit = 29
            elif code == "DRSE":
                pass
            elif code == "DRSD":
                pass
            elif code == "TMPT":
                byteCode = byteCode + 'B'
                endBit = 29
            elif code == "CHQF":
                pass
            elif code == "RCWN":
                byteCode = byteCode + 'B'
                endBit = 29
            elif code == "PENA":
                byteCode = byteCode + 'BBBBBBB'
                endBit = 35
            elif code == "SPTP":
                byteCode = byteCode + 'BfBBBf'
                endBit = 40
            elif code == "STLG":
                byteCode = byteCode + 'B'
                endBit = 29
            elif code == "LGOT":
                pass
            elif code == "DTSV":
                byteCode = byteCode + 'B'
                endBit = 29
            elif code == "SGSV":
                byteCode = byteCode + 'B'
                endBit = 29
            elif code == "FLBK":
                byteCode = byteCode + 'Lf'
                endBit = 36
            
            #for x in range(22):
            #    byteCode = byteCode + 'IIHHfffBBBBBBBBBBBBBBHHB'
            #byteCode = byteCode + 'BB'
            
            if endBit is not None:
                interpret = struct.unpack(byteCode, message[28:endBit])
                #print(interpret)
                unpacked = (code,) + interpret
            else:
                unpacked = (code,)

            #print(unpacked)
            #print("Break")

            # Full message send
            #MESSAGE = "{},{},{},{}".format(header + unpacked)
            MESSAGE = "{}".format(json.dumps(["packet_03", header, unpacked, timeStamp]));
            #MESSAGE = str(header + unpacked)
            #print(MESSAGE)
            sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))

            count = count + 1
            if count % 100 == 0:
                print("    Packet 03 messages sent: " + str(count))




