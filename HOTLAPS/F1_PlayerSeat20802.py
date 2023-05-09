# Records messages for a set number of seconds, then writes a file

import sys
import socket
import time
import struct
import random

fileName = sys.argv[1]
print("Playback of this file:", fileName)


randomSeshID = False
if len(sys.argv) > 2:
    if sys.argv[2] == "random":
        randomSeshID = True

MESSAGE = "23,567,32,4356,456,132,4353467" #init message

data = 0 #artificial data

UDP_IP = "127.0.0.1" #standard ip udp (localhost)
#UDP_IP = "132.145.38.38" #instance IP on cloud, load balancer in UK South
#UDP_IP = "132.145.30.140" #instance IP on cloud, load balancer in UK South
#UDP_IP = "129.153.176.88" #instance in ASBURN
#UDP_IP = "130.61.110.184" #standard ip udp (localhost)
#UDP_IP = "109.37.153.154" #wouter laptop
#UDP_IP = "10.146.66.184" #Roving Edge Red

UDP_PORT_1 = 20802   #chosen port to instance 

# Socket to Cloud instance listener - initiate socket and send first message
sockSession = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
try:
    sockSession.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT_1))
except:
    print('Initial message failed!')


#Read file into memory
f = open(fileName, "rb")
data = f.read()
f.close()

lines = data.split(b'NEWLINE')
#print(data)
#print(len(lines))

keepGoing = True

#startTime = time.time()
#print("Start Time")

count = 1

while keepGoing:
    
    # Choose a new random sessionID unit64
    newSeshIDBytes = None
    if randomSeshID:
        newSeshID = random.getrandbits(64)
        newSeshIDBytes = struct.pack('Q', newSeshID)
        #print(newSeshID, newSeshIDBytes)

    print("Starting: " + str(count) + " times through.")
    if randomSeshID:
        print("    using this new SessionID: ", struct.unpack('<Q', newSeshIDBytes)[0])
    
    startTime = time.time()
    print("    using this start time: ", startTime)
    offsetTime = 0
    backDateTime = 0

    lineCount = 0
    
    for line in lines:
        if lineCount == 0:
            offsetTime = struct.unpack('<f', line[14:18])[0]
            print("    offset time: ", offsetTime)
            backDateTime = startTime - offsetTime
            print("    back date time:", backDateTime)
        
        lineCount = lineCount + 1
        
        

        # Check length
        if len(line) < 24:
            print("Bad message, length: ", len(line))
            continue

        #header = struct.unpack('<HBBBBQfIBB', line[0:24])
        #sessionID = struct.unpack('<Q', line[6:14])
        #print("Before:", header, sessionID)
        #messageFrame = struct.unpack('<I', line[18:22])[0]
        #deltaFrame = messageFrame - lastMessageFrame
        #deltaTimeStamp = messageTimeStamp - lastMessageTimeStamp
        #print(messageFrame, deltaFrame, messageTimeStamp, deltaTimeStamp)
        #lastMessageFrame = messageFrame
        #lastMessageTimeStamp = messageTimeStamp        

        messageTimeStamp = struct.unpack('<f', line[14:18])[0]
        currentOffsetTime = time.time() - backDateTime
        #print(time.time() - backDateTime, messageTimeStamp)
        if currentOffsetTime < messageTimeStamp:
            #print("     sleeping:", messageTimeStamp - currentOffsetTime)
            time.sleep(messageTimeStamp - currentOffsetTime)
       
            

        #print("Sending message:", struct.unpack('<b', line[5:6])[0], messageTimeStamp)
        
        # Replace SessionID if random
        if randomSeshID:
            newline = line[:6] + newSeshIDBytes + line[14:]
            #header = struct.unpack('<HBBBBQfIBB', newline[0:24])
            #sessionID = struct.unpack('<Q', newline[6:14])
            #print("After:", header, sessionID)

            #Send to IP and port
            sockSession.sendto(newline, (UDP_IP, UDP_PORT_1))
        
        else:
            #Send to IP and port
            sockSession.sendto(line, (UDP_IP, UDP_PORT_1))

        
    
    count = count + 1

