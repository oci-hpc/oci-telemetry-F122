# Starts the Splitter and all the TXX packet types on different threads
# Records into a file if a "record" is given in the arguments list
#     ---Records a subset of packets if "min" is given in the arguments list
# Splits each new session by sessionID if "splitsession" is given in the arguments list

import sys
from threading import Thread
import subprocess


record = False
minimalData = False
splitSession = False

for item in sys.argv:
    if item == "record":
        record = True
    if item == "min":
        minimalData = True
    if item == "splitsession":
        splitSession = True



# Create threads
split = None
recorder = None

if record is True:
    split = Thread(target=subprocess.run, args=(["python3", "F1_Splitter.py", "record"],))
    
    recordArgs = ["python3", "F1_Recorder.py"]
    if minimalData is True:
        recordArgs.append("min")
    if splitSession is True:
        recordArgs.append("splitsession")
    
    recorder = Thread(target=subprocess.run, args=(recordArgs,))
else:
    split = Thread(target=subprocess.run, args=(["python3", "F1_Splitter.py"],))


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
split.start()

if split is None:
    print("Splitter didn't start, exiting")
    exit()

if record:
    recorder.start()


t00.start()
t01.start()
t02.start()
t03.start()
t04.start()
t05.start()
t06.start()
t07.start()
t08.start()
t09.start()
t10.start()
t11.start()

# Join threads (wait till they are all finished, which is never)
#split.join()#
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

