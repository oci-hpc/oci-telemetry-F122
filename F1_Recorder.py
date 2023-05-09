# Records messages for a set number of seconds, then writes a file

import sys
import socket
import time
import struct
from threading import Thread
from queue import Queue
#import subprocess
from datetime import datetime




# Dedicated file writing task
def file_writer(fileName, queue):
    # open the file
    with open(fileName, 'ab') as file:
        # run until the event is set
        while True:
            # get a line of text from the queue
            line = queue.get()
            # check if we are done
            if line is None:
                # exit the loop
                break
            # write it to file
            file.write(line)
            file.write("NEWLINE".encode('utf-8'))
            # flush the buffer
            file.flush()
            # mark the unit of work complete
            queue.task_done()
    # mark the exit signal as processed, after the file was closed
    queue.task_done()
 
# Task for worker threads
def task(number, queue, messageBuffer):
    # task loop
    #size= struct.unpack('<i', messageBuffer[number][0:4])
    #print("Task number", number)
    #queue.put(f'Thread {number} got {size}.\n')
    queue.put(messageBuffer[number])
    #for i in range(1000):
    #    # generate random number between 0 and 1
    #    value = random()
    #    # put the result in the queue
    #    queue.put(f'Thread {number} got {value}.\n')


# Write the messageBuffer to file on separate threads
def flushBufferToFile(messageBuffer,fileName):
    print("Flushing buffer to file at:" + str(datetime.now()))
    startingTime = time.time()
    #print(len(messageBuffer))
    # Create the shared queue
    queue = Queue()

    # Create and start the file writer thread
    writer_thread = Thread(target=file_writer, args=(fileName,queue), daemon=True)
    writer_thread.start()

    ## Configure worker threads, 1 for each message in the buffer
    threads = [Thread(target=task, args=(i,queue, messageBuffer)) for i in range(len(messageBuffer))]

    # Start Threads
    for thread in threads:
        thread.start()
    # Wait for threads to finish
    for thread in threads:
        thread.join()
    # Signal the file writer thread that we are done
    queue.put(None)
    # Wait for all tasks in the queue to be processed
    queue.join()
    endingTime = time.time()
    print("Time to write file:" + str(f'{(endingTime - startingTime):.3f}'))

def buildFilePath(withSessionID, sessionID):
    filepath = "F1_Output_"
    filepath = filepath + str(datetime.now().year) + "-"
    filepath = filepath + str(datetime.now().month) + "-"
    filepath = filepath + str(datetime.now().day) + "-"
    filepath = filepath + str(datetime.now().hour) + "-"
    filepath = filepath + str(datetime.now().minute) + "-"
    filepath = filepath + str(datetime.now().second)
    if withSessionID:
        filepath = filepath + "-" + str(sessionID)
    filepath = filepath + ".dat"

    return filepath


minimalData = False
splitSesh = False
for item in sys.argv:
    if item == "min":
        minimalData = True
    if item == "splitsession":
        splitSesh = True

# Fake initial message
MESSAGE = "23,567,32,4356,456,132,4353467" #init message
data = 0 #artificial data

#Receiver socket from game UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.settimeout(15)
server_socket.bind(('', 20776))

messageBuffer = []
sessionID = None

# Build the shared filename (path) from time this recorder starts
filepath = buildFilePath(False, None)

print("F1_Recording to this file prefix:" + filepath)




keepGoing = True
bufferFlushSize = 1500 #messages
minFlushTime = 30 #seconds
timeOfLastFlush = time.time()

while keepGoing:
  
    message = None
    try:
        message, address = server_socket.recvfrom(1024000)
    except:
        print("Timeout: waiting for more data.", str(datetime.now()))

    
    # If we want to mark each message with length
    #messageLength = len(message)
    #messageLengthByte = messageLength.to_bytes(length=4,byteorder='little',signed=False)
    #print(messageLength, messageLengthByte)
    #print(message)
    #server_socket.sendto(message, address)
    #messageBuffer.append(messageLengthByte + message)
    
    # If we split files by session ID then we need to keep track of sessionID as it changes and update the file name
    if message is not None:
        if splitSesh:
            newSessionID = struct.unpack('<Q', message[6:14])[0]
            if newSessionID != sessionID:
                print(newSessionID, sessionID)
                # Flush buffer
                if sessionID is not None:
                    bufferToFlush = messageBuffer
                    flushBufferToFile(bufferToFlush, filepath)
                    messageBuffer = []
                    timeOfLastFlush = time.time()

                # Reset Session ID and filepath
                sessionID = newSessionID
                filepath = buildFilePath(splitSesh, sessionID)
                print("Updated file name: ", filepath)


    # Just the message
    # Meters each message if minimum data is requested
    if message is not None:
        if minimalData:
            #okPackets = [1,2,4,6,9,11]
            #if message[5:6] == b'\x00':
            #    messageBuffer.append(message)
            if message[5:6] == b'\x01':
                messageBuffer.append(message)
            elif message[5:6] == b'\x02':
                messageBuffer.append(message)
            #elif message[5:6] == b'\x03':
            #    messageBuffer.append(message)
            elif message[5:6] == b'\x04':
                messageBuffer.append(message)
            #elif message[5:6] == b'\x05':
            #    messageBuffer.append(message)
            elif message[5:6] == b'\x06':
                messageBuffer.append(message)
            #elif message[5:6] == b'\x07':
            #    messageBuffer.append(message)
            #elif message[5:6] == b'\x08':
            #    messageBuffer.append(message)
            elif message[5:6] == b'\x09':
                messageBuffer.append(message)
            #elif message[5:6] == b'\n':
            #    messageBuffer.append(message)
            elif message[5:6] == b'\x0b':
                messageBuffer.append(message)
        
        
        else:
            messageBuffer.append(message)
    
    

    if len(messageBuffer) >= bufferFlushSize:
        bufferToFlush = messageBuffer
        flushBufferToFile(bufferToFlush, filepath)
        messageBuffer = []
        timeOfLastFlush = time.time()
    elif time.time() - timeOfLastFlush >= minFlushTime:
        if len(messageBuffer) > 0:
            bufferToFlush = messageBuffer
            flushBufferToFile(bufferToFlush, filepath)
            messageBuffer = []
            timeOfLastFlush = time.time()



