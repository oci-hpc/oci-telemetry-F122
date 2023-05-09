# Records messages for a set number of seconds, then writes a file

import sys
import socket
import time
import struct
from threading import Thread
from queue import Queue
#import subprocess
from datetime import datetime
#import oci
from base64 import b64encode, b64decode

# Postgres DB stuff
import psycopg2
from psycopg2 import sql
from config import config

# Postgres insert sessionID and lapnumber (unique record)
# timestamp, sessionID, port, lapnumber, lapTimeMS, sector1MS, sector2MS, sector3MS
def insert_hotlap(tableName, timestamp, sessionID, port, lapnumber, lapTimeMS, sector1MS, sector2MS, sector3MS):
    """ insert a new hotlap into the hotlaps table """
    query = sql.SQL("INSERT INTO {table} (timestamp, sessionid, port, lapnumber, laptimems, sector1ms, sector2ms, sector3ms) VALUES(%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING").format(table=sql.Identifier(tableName))
#    sql = """INSERT INTO %s(timestamp, sessionid, port, lapnumber, laptimems, sector1ms, sector2ms, sector3ms)
#             VALUES(%s,%s,%s,%s,%s,%s,%s,%s) 
#             ON CONFLICT DO NOTHING;"""
    conn = None
    hotlap_id = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(query, (timestamp, sessionID, port, lapnumber, lapTimeMS, sector1MS, sector2MS, sector3MS))
        # get the generated id back
        #hotlap_id = cur.fetchone()[0]
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return hotlap_id


# Postgres update trackID
# sessionID, trackID
def update_trackID(tableName, sessionID, trackID):
    """ update a hotlap with trackID into the hotlaps table """
    query = sql.SQL("UPDATE {table} SET trackid = %s WHERE sessionid = %s").format(table=sql.Identifier(tableName))
    #sql = """UPDATE %s SET trackid = %s
    #            WHERE sessionid = %s"""
    conn = None
    hotlap_id = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(query, (trackID, sessionID))
        # get the generated id back
        #hotlap_id = cur.fetchone()[0]
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return hotlap_id

# Postgres update participant
# sessionID, participant
def update_participant(tableName, sessionID, participant):
    """ update a hotlap with trackID into the hotlaps table """
    query = sql.SQL("UPDATE {table} SET participant = %s WHERE sessionid = %s").format(table=sql.Identifier(tableName))
    #sql = """UPDATE %s SET participant = %s
    #            WHERE sessionid = %s"""
    conn = None
    hotlap_id = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(query, (participant, sessionID))
        # get the generated id back
        #hotlap_id = cur.fetchone()[0]
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return hotlap_id


listeningPort = 20777

for item in sys.argv:
    if "port" in item:
        if len(item.split("=")) > 1:
            if item.split("=")[1].isdigit():
                listeningPort = int(item.split("=")[1])
                print("HotLaps: Game data is on port:", listeningPort)





#Receiver socket from splitter
UDP_PORT = 20774
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.settimeout(15)
server_socket.bind(('', UDP_PORT))

print("    F1_HotLaps receiving daa from splitter on port: ", UDP_PORT)

keepGoing = True

counterLap = 0
counterLapSent = 0
counterTrack = 0
counterTrackSent = 0
counterParticipants = 0
counterParticipantsSent = 0


while keepGoing:
  
    message = None
    try:
        message, address = server_socket.recvfrom(1024000)
    except:
        print("Timeout: waiting for more data.", str(datetime.now()))


    # Just the hotlaps messages
    # Meters each message if hotlap data is requested
    if message is not None:
        
        # Check minimal length for header
        if len(message) < 24:
            print("Bad message, length: ", len(message))
            continue
 
        # This is the session history packet with laps, packet 11
        if message[5:6] == b'\x0b':

            # Check message is correct length, per documentation
            if len(message) != 1155:
                print("Bad packet 11 message, should be 1155, was length: ", len(message))
                continue

            counterLap = counterLap + 1
            # Unpack and send for now
            # Header
            header = struct.unpack('<HBBBBQfIBB', message[0:24])
            #print(header)
            sessionID = header[5]
            timeInSession = header[6]

            # Bytes
            byteCode = '<BBBBBBB'
            for x in range(100):
                byteCode = byteCode + 'IHHHB'
            for x in range(8):
                byteCode = byteCode + 'BBB'

            unpacked = struct.unpack(byteCode, message[24:1191])
        
            player1Index = header[8]
            thisDataIndex = unpacked[0]
            startIndex = 7
            slugSize = 5
            
            #print("P1 = :", player1Index, "This data index:", thisDataIndex)
            if player1Index == thisDataIndex:
                #print(unpacked)
                bestLapTimeLapNum = unpacked[3]
                if bestLapTimeLapNum > 0 and bestLapTimeLapNum <= 100:
                    # Grab just the fastest lap
                    #print("    Fastest Lap Number: ", unpacked[3])
                    #print(unpacked[0], unpacked[1], unpacked[2], unpacked[3], unpacked[4], unpacked[5], unpacked[6], unpacked[7])
                
                    lapTime   = unpacked[startIndex + (bestLapTimeLapNum - 1) * slugSize]
                    sector1   = unpacked[startIndex + (bestLapTimeLapNum - 1) * slugSize + 1]
                    sector2   = unpacked[startIndex + (bestLapTimeLapNum - 1) * slugSize + 2]
                    sector3   = unpacked[startIndex + (bestLapTimeLapNum - 1) * slugSize + 3]
                    validFlag = unpacked[startIndex + (bestLapTimeLapNum - 1) * slugSize + 4]

                    timeStamp = int(time.time() * 1000)

                    if validFlag == 15:
                        if lapTime > 0 and sector1 > 0 and sector2 > 0 and sector3 > 0:
                            print("    Fastest Lap Number: ", bestLapTimeLapNum, lapTime/1000, sector1/1000, sector2/1000, sector3/1000)
                            #print(timeStamp, sessionID, listeningPort, bestLapTimeLapNum, lapTime, sector1, sector2, sector3, validFlag)
                            insert_hotlap("hotlaps", timeStamp, sessionID, listeningPort, bestLapTimeLapNum, lapTime, sector1, sector2, sector3)
                            insert_hotlap("hotlaps_archive", timeStamp, sessionID, listeningPort, bestLapTimeLapNum, lapTime, sector1, sector2, sector3)
                            counterLapSent = counterLapSent + 1
                            #print(unpacked)
                else:
                    # Have to loop through and find the fastest valid lap
                    
                    lapTime   = 0
                    sector1   = 0
                    sector2   = 0
                    sector3   = 0
                    validFlag = 0

                    fastestValidLapIndex = 0
                    fastestLapTimeSoFar = 0
                    for i in range(0,100):
                        validFlag = unpacked[startIndex + (i * slugSize) + 4]
                        if validFlag == 15:
                            lapTime = unpacked[startIndex + (i * slugSize)]
                            if lapTime > 0:
                                if fastestValidLapIndex == 0:
                                    fastestValidLapIndex = i + 1
                                    fastestLapTimeSoFar = lapTime
                                else:
                                    if lapTime > 0 and lapTime < fastestLapTimeSoFar:
                                        fastestValidLapIndex = i + 1
                                        fastestLapTimeSoFar = lapTime
                    
                    if fastestValidLapIndex < 1 or fastestValidLapIndex > 100:
                        print("---No valid laps so far...", "time in session:", timeInSession)
                    else:
                        #print("    Fastest Lap Number: ", fastestValidLapIndex)
                        lapTime   = unpacked[startIndex + (fastestValidLapIndex - 1) * slugSize]
                        sector1   = unpacked[startIndex + (fastestValidLapIndex - 1) * slugSize + 1]
                        sector2   = unpacked[startIndex + (fastestValidLapIndex - 1) * slugSize + 2]
                        sector3   = unpacked[startIndex + (fastestValidLapIndex - 1) * slugSize + 3]
                        validFlag = unpacked[startIndex + (fastestValidLapIndex - 1) * slugSize + 4]

                        timeStamp = int(time.time() * 1000)

                        if validFlag == 15:
                            if lapTime > 0 and sector1 > 0 and sector2 > 0 and sector3 > 0:
                                #print(timeStamp, sessionID, listeningPort, fastestValidLapIndex, lapTime, sector1, sector2, sector3, validFlag)
                                print("    Fastest Lap Number: ", fastestValidLapIndex, lapTime/1000, sector1/1000, sector2/1000, sector3/1000)
                                insert_hotlap("hotlaps", timeStamp, sessionID, listeningPort, fastestValidLapIndex, lapTime, sector1, sector2, sector3)
                                insert_hotlap("hotlaps_archive", timeStamp, sessionID, listeningPort, fastestValidLapIndex, lapTime, sector1, sector2, sector3)
                                counterLapSent = counterLapSent + 1
                                #print(unpacked)
            
            if counterLap > 0 and counterLap % 500 == 0:
                print("    Packet 11 messages received: " + str(counterLap))
            if counterLapSent > 0 and counterLapSent % 500 == 0:
                print("    Packet 11 messages sent to DB: " + str(counterLapSent))

        # This is the trackID
        elif message[5:6] == b'\x01':
            
            # Check message is correct length, per documentation
            if len(message) != 632:
                continue

            counterTrack = counterTrack + 1


            # Unpack and send for now
            # Header
            header = struct.unpack('<HBBBBQfIBB', message[0:24])
            #print(header)
            sessionID = header[5]

            packet_part_1 = struct.unpack('<BbbBHBbBHHBBBBBB', message[24:43])
            
            trackID = packet_part_1[6]

            if trackID >= 0:
                update_trackID("hotlaps", sessionID, trackID)
                update_trackID("hotlaps_archive", sessionID, trackID)
                #print("trackID", trackID)
                counterTrackSent = counterTrackSent + 1

            if counterTrack > 0 and counterTrack % 500 == 0:
                print("    Packet 01 messages received: " + str(counterTrack))
            if counterTrackSent > 0 and counterTrackSent % 500 == 0:
                print("    Packet 01 messages sent to DB: " + str(counterTrackSent))
        
        # This is the participants
        elif message[5:6] == b'\x04':
            
            # Check message is correct length, per documentation
            if len(message) != 1257:
                continue

            counterParticipants = counterParticipants + 1
            # Unpack and send for now
            # Header
            header = struct.unpack('<HBBBBQfIBB', message[0:24])
            #print(header)
            sessionID = header[5]
            player1Index = header[8]

            # Bytes - starts with numCars B
            byteCode = '<B'
            for x in range(22):
                byteCode = byteCode + 'BBBBBBB48sB'
        

            unpacked = struct.unpack(byteCode, message[24:1257])
            # Decode Driver Name strings
            unpackedList = list(unpacked)
            #print(unpackedList[8].decode('utf8', 'strict'), "hey")
            position = 7
            nameList = []
            for x in range(22):
                nameList.append(str(unpackedList[(x * 9) + position + 1].decode('utf8', 'strict').replace('\x00', '')))
            for x in range(22):
                unpackedList[(x * 9) + position + 1] = nameList[x]
            unpacked = tuple(unpackedList)
                
            participant = unpacked[1 + (player1Index * 9) + position]

            if len(participant) > 0:
                update_participant("hotlaps", sessionID, participant)
                update_participant("hotlaps_archive", sessionID, participant)
                #print(sessionID, participant)
                counterParticipantsSent = counterParticipantsSent + 1

            #lapInfo = unpacked[player1Index * slugSize: player1Index * slugSize + slugSize]


            if counterParticipants > 0 and counterParticipants % 500 == 0:
                print("    Packet 04 messages received: " + str(counterParticipants))
            if counterParticipantsSent > 0 and counterParticipantsSent % 500 == 0:
                print("    Packet 04 messages sent to DB: " + str(counterParticipantsSent))





