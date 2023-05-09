# Starts the Splitter and all the TXX packet types on different threads
# Records into a file if a "record" is given in the arguments list
#     ---Records a subset of packets if "min" is given in the arguments list
# Splits each new session by sessionID if "splitsession" is given in the arguments list

import sys
from threading import Thread
import subprocess


# Options from arguments
port = 20777

# --- RECORDING DATA ---
# Turn on record to file
record = False
# Split sessions into separate files
splitSession = False
# Turn on stream to OCI-Streaming
stream = False
# Minimal data for hot laps, lap and sector times only
hotlaps = False


# --- METERING DATA ---
# Minimal data for a select number of traces
minimalData = False

# --- LIVE TELEMETRY ---
# Turn off send to OpenMCT
liveTelemetry = True


for item in sys.argv:
    # --- RECORDING ---
    if "record" in item.lower():
        record = True
    if "stream" in item.lower():
        stream = True
    if "splitsession" in item.lower():
        splitSession = True
    if "hotlap" in item.lower():
        hotlaps = True
    if "port" in item:
        if len(item.split("=")) > 1:
            if item.split("=")[1].isdigit():
                port = int(item.split("=")[1])
                print("Ingestor: Splitter will listening for game data on port:", port)
    
    # --- METERING ---
    if "min" in item.lower():
        minimalData = True
    
    # --- LIVE TELEMETRY ---
    if "notelemetry" in item.lower():
        liveTelemetry = False
    



# Create threads
splitter = None
recorder = None
streamer = None
hotlapper = None


splitPort = "port=" + str(port)
splitterArgs = ["python3", "F1_Splitter.py", splitPort]


# --- RECORDING TO FILE
if record is True:
    splitterArgs.append("record")
   
    recordArgs = ["python3", "F1_Recorder.py"]
    if minimalData is True:
        recordArgs.append("min")
    if splitSession is True:
        recordArgs.append("splitsession")
    if hotlaps is True:
        recordArgs.append("hotlaps")
    
    recorder = Thread(target=subprocess.run, args=(recordArgs,))

# --- RECORDING TO STREAM
if stream is True:
    splitterArgs.append("stream")

    streamerArgs = ["python3", "F1_Streamer.py"]
    #if minimalData is True:
    #    recordArgs.append("min")
    #if splitSession is True:
    #    recordArgs.append("splitsession")
    
    streamer = Thread(target=subprocess.run, args=(streamerArgs,))

# --- RECORDING HOTLAPS ONLY
if hotlaps is True:
    splitterArgs.append("hotlap")

    hotlapPort = "port=" + str(port)
    hotlapsArgs = ["python3", "F1_HotLaps.py", hotlapPort]
    #if minimalData is True:
    #    recordArgs.append("min")
    #if splitSession is True:
    #    recordArgs.append("splitsession")
    
    hotlapper = Thread(target=subprocess.run, args=(hotlapsArgs,))

# --- NO LIVE TELEMETRY
if liveTelemetry is False:
    splitterArgs.append("notelemetry")

#else:
#    split = Thread(target=subprocess.run, args=(["python3", "F1_Splitter.py"],))

# --- Start Splitter
splitter = Thread(target=subprocess.run, args=(splitterArgs,))
#split = Thread(target=subprocess.run, args=(["python3", "F1_Splitter.py", "record"],))



# --- LIVE TELEMETRY
t00 = None
t01 = None
t02 = None
t03 = None
t04 = None
t05 = None
t06 = None
t07 = None
t08 = None
t09 = None
t10 = None
t11 = None

if liveTelemetry:
    t00 = Thread(target=subprocess.run, args=(["python3", "F1_T00_Motion_Feed.py"],))
    t01 = Thread(target=subprocess.run, args=(["python3", "F1_T01_Session_Feed.py"],))
    t02 = Thread(target=subprocess.run, args=(["python3", "F1_T02_Lap_Data_Feed.py"],))
    t03 = Thread(target=subprocess.run, args=(["python3", "F1_T03_Event_Feed.py"],))
    t04 = Thread(target=subprocess.run, args=(["python3", "F1_T04_Participants_Feed.py"],))
    t05 = Thread(target=subprocess.run, args=(["python3", "F1_T05_Car_Setups_Feed.py"],))
    t06 = Thread(target=subprocess.run, args=(["python3", "F1_T06_Car_Telemetry_Feed.py"],))
    t07 = Thread(target=subprocess.run, args=(["python3", "F1_T07_Car_Status_Feed.py"],))
    t08 = Thread(target=subprocess.run, args=(["python3", "F1_T08_Final_Classification_Feed.py"],))
    t09 = Thread(target=subprocess.run, args=(["python3", "F1_T09_Lobby_Info_Feed.py"],))
    t10 = Thread(target=subprocess.run, args=(["python3", "F1_T10_Car_Damage_Feed.py"],))
    t11 = Thread(target=subprocess.run, args=(["python3", "F1_T11_Session_History_Feed.py"],))

# Start threads
splitter.start()

if splitter is None:
    print("Splitter didn't start, exiting")
    exit()

if record:
    recorder.start()
    if recorder is None:
        print("Recorder didn't start.")


if stream:
    streamer.start()
    if streamer is None:
        print("Streamer didn't start.")

if hotlaps:
    hotlapper.start()
    if hotlapper is None:
        print("HotLapper didn't start.")

# --- Live Telemetry Threads ---
if liveTelemetry:
    if t00 is not None:
        t00.start()
    if t01 is not None:
        t01.start()
    if t02 is not None:
        t02.start()
    if t03 is not None:
        t03.start()
    if t04 is not None:
        t04.start()
    if t05 is not None:
        t05.start()
    if t06 is not None:
        t06.start()
    if t07 is not None:
        t07.start()
    if t08 is not None:
        t08.start()
    if t09 is not None:
        t09.start()
    if t10 is not None:
        t10.start()
    if t11 is not None:
        t11.start()


# Join threads (wait till they are all finished, which is never)
#splitter.join()#
#recorder.join()
#t00.join()
#t01.join()
#t02.join()
#t03.join()
#t04.join()
#t05.join()
#t06.join()
#t07.join()
#t08.join()
#t09.join()
#t10.join()
#t11.join()

