# Takes data from F122 and splits messages by message type found in header bit.
# Sends to other ports that read the messages.
# Listens on port from F1 game, UDP: UDP_PORT
# Sends all messages to the recorder port if "record" is in the arguments list

import socket
import time
import struct
import sys
from datetime import datetime



record = False
stream = False
hotlap = False
port = 20777
liveTelemetry = True

for item in sys.argv:
    if "record" in item.lower():
        record = True
    if "stream" in item.lower():
        stream = True
    if "hotlap" in item.lower():
        hotlap = True
    if "port" in item:
        if len(item.split("=")) > 1:
            if item.split("=")[1].isdigit():
                port = int(item.split("=")[1])
                print("Splitter: Listening for game data on port:", port)
    if "notelemetry" in item.lower():
        liveTelemetry = False




# Sends data to these ports:
UDP_IP = "127.0.0.1" #standard ip udp (localhost)
UDP_PORT = 20777
if port != 20777:
    UDP_PORT = port

UDP_PORT_RECORD = 20776 #Recorder
UDP_PORT_STREAM = 20775 #Streamer
UDP_PORT_HOTLAP = 20774 #HotLapper



UDP_PORT_0  = 20778   #Type 0, Motion
UDP_PORT_1  = 20779   #Type 1, Session
UDP_PORT_2  = 20780   #Type 2, Lap Data
UDP_PORT_3  = 20781   #Type 3, Event
UDP_PORT_4  = 20782   #Type 4, Participants
UDP_PORT_5  = 20783   #Type 5, Car Setups
UDP_PORT_6  = 20784   #Type 6, Car Telemetry
UDP_PORT_7  = 20785   #Type 7, Car Status
UDP_PORT_8  = 20786   #Type 8, Final Classification
UDP_PORT_9  = 20787   #Type 9, Lobby Info
UDP_PORT_10 = 20788   #Type 10, Car Damage
UDP_PORT_11 = 20789   #Type 11, Session History

MESSAGE = "23,567,32,4356,456,132,4353467" #init message

# Type R - initiate socket and send first message
sock_R = None
if record:
    
    sock_R = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
    try:
        sock_R.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT_RECORD))
    except:
        print('Initial message failed -- Recorder')

# Type S - initiate socket and send first message
sock_S = None
if stream:
    
    sock_S = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
    try:
        sock_S.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT_STREAM))
    except:
        print('Initial message failed -- Streamer')

# Type H - initiate socket and send first message
sock_H = None
if hotlap:
    
    sock_H = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
    try:
        sock_H.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT_HOTLAP))
    except:
        print('Initial message failed -- HotLapper')


sock_0 = None
sock_1 = None
sock_2 = None
sock_3 = None
sock_4 = None
sock_5 = None
sock_6 = None
sock_7 = None
sock_8 = None
sock_9 = None
sock_10 = None
sock_11 = None

if liveTelemetry:
    # Type 0 - initiate socket and send first message
    sock_0 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
    try:
        sock_0.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT_0))
    except:
        print('Initial message failed!')

    # Type 1 - initiate socket and send first message
    sock_1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
    try:
        sock_1.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT_1))
    except:
        print('Initial message failed!')

    # Type 2 - initiate socket and send first message
    sock_2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
    try:
        sock_2.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT_2))
    except:
        print('Initial message failed!')

    # Type 3 - initiate socket and send first message
    sock_3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
    try:
        sock_3.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT_3))
    except:
        print('Initial message failed!')

    # Type 4 - initiate socket and send first message
    sock_4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
    try:
        sock_4.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT_4))
    except:
        print('Initial message failed!')

    # Type 5 - initiate socket and send first message
    sock_5 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
    try:
        sock_5.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT_5))
    except:
        print('Initial message failed!')

    # Type 6 - initiate socket and send first message
    sock_6 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
    try:
        sock_6.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT_6))
    except:
        print('Initial message failed!')

    # Type 7 - initiate socket and send first message
    sock_7 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
    try:
        sock_7.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT_7))
    except:
        print('Initial message failed!')

    # Type 8 - initiate socket and send first message
    sock_8 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
    try:
        sock_8.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT_8))
    except:
        print('Initial message failed!')

    # Type 9 - initiate socket and send first message
    sock_9 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
    try:
        sock_9.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT_9))
    except:
        print('Initial message failed!')

    # Type 10 - initiate socket and send first message
    sock_10 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
    try:
        sock_10.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT_10))
    except:
        print('Initial message failed!')

    # Type 11 - initiate socket and send first message
    sock_11 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
    try:
        sock_11.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT_11))
    except:
        print('Initial message failed!')


#Receiver socket from game UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.settimeout(15)
server_socket.bind(('', UDP_PORT))

count = 0

while True:

    message = None
    try:
        message, address = server_socket.recvfrom(1024000)
    except KeyboardInterrupt:
        print("User stopped: F1_Splitter.")
        exit()
    except:
        print("Timeout: Splitter waiting for more data from port:", UDP_PORT, str(datetime.now()))   
    #message, address = server_socket.recvfrom(1024000)
    #print(message)
    #server_socket.sendto(message, address)
    

    if message is not None:

        #Message must be at least 24 bytes per documentation
        #Throw away any message shorter than 24
        if len(message) < 24:
            print("Bad message, length: ", len(message))
            continue

        # --- RECORDING ---
        if record:
            sock_R.sendto(message, (UDP_IP, UDP_PORT_RECORD))
        if stream:
            sock_S.sendto(message, (UDP_IP, UDP_PORT_STREAM))
        if hotlap:
            sock_H.sendto(message, (UDP_IP, UDP_PORT_HOTLAP))


        # --- LIVE TELEMETRY ---
        if liveTelemetry:
            if message[5:6] == b'\x00':
                #print("Packet 0")
                sock_0.sendto(message, (UDP_IP, UDP_PORT_0))

            elif message[5:6] == b'\x01':
                #print("Packet 1")
                sock_1.sendto(message, (UDP_IP, UDP_PORT_1))

            elif message[5:6] == b'\x02':
                #print("Packet 2")
                sock_2.sendto(message, (UDP_IP, UDP_PORT_2))

            elif message[5:6] == b'\x03':
                #print("Packet 3")
                sock_3.sendto(message, (UDP_IP, UDP_PORT_3))

            elif message[5:6] == b'\x04':
                #print("Packet 4")
                sock_4.sendto(message, (UDP_IP, UDP_PORT_4))
    
            elif message[5:6] == b'\x05':
                #print("Packet 5")
                sock_5.sendto(message, (UDP_IP, UDP_PORT_5))
    
            elif message[5:6] == b'\x06':
                #print("Packet 6")
                sock_6.sendto(message, (UDP_IP, UDP_PORT_6))
    
            elif message[5:6] == b'\x07':
                #print("Packet 7")
                sock_7.sendto(message, (UDP_IP, UDP_PORT_7))
    
            elif message[5:6] == b'\x08':
                #print("Packet 8")
                sock_8.sendto(message, (UDP_IP, UDP_PORT_8))

            elif message[5:6] == b'\x09':
                #print("Packet 9")
                sock_9.sendto(message, (UDP_IP, UDP_PORT_9))

            elif message[5:6] == b'\n':
                #print("Packet 10")
                sock_10.sendto(message, (UDP_IP, UDP_PORT_10))
    
            elif message[5:6] == b'\x0b':
                #print("Packet 11")
                sock_11.sendto(message, (UDP_IP, UDP_PORT_11))


        if count % 1000 == 0:
            print ("Total message count: " +  str(count))

        count = count + 1


