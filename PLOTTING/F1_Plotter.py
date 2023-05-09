# Tries to pick out laps and puts into to some arrays,
# Then builds some plots

import sys
import socket
import time
import struct
from threading import Thread
from queue import Queue
#import subprocess
from datetime import datetime
import plotly.express as px
import pandas as pd
import os
from plotly.subplots import make_subplots
import plotly.graph_objects as go



fileName = sys.argv[1]
print("Plotting of this file:", fileName)

lapOfInterest = None
carOfInterest = None
traces = False
outputDir = "PLOTS"

for item in sys.argv:
    if item.startswith("lap"):
        lapOfInterest = int(item.replace("lap", ""))

    if item.startswith("car"):
        carOfInterest = int(item.replace("car", ""))
    
    if item.startswith("trace"):
        traces = True
    


print("    Lap of interest: ", lapOfInterest, " Car of interest: ", carOfInterest)

#Read file into memory
f = open(fileName, "rb")
data = f.read()
f.close()

lines = data.split(b'NEWLINE')

print("    File read and split. Starting data extraction...")

speedTrace = []
gearTrace = []
throttleTrace = []
brakeTrace = []
distanceTrace = []
lapTimeTrace = []



lineCount = 0
lastLineTimestamp = 0
lastframeID = 0
for line in lines:
    
    # Check length
    if len(line) < 24:
        print("Bad message, length: ", len(line))
        continue

    if line is not None:
        #if message[5:6] == b'\x00':
        #    messageBuffer.append(message)
        #if message[5:6] == b'\x01':
        #    messageBuffer.append(message)

        #Print every frameID for every Telemetry Packet

        header = struct.unpack('<HBBBBQfIBB', line[0:24])

        #thisFrameID = header[7]
        #if thisFrameID - lastframeID > 1:
        #    print("Skipped a frame:", thisFrameID, lastframeID)
        #lastframeID = thisFrameID

        #if header[4] == 3:
        #    #print(header[4], header[7], header[6])



        thisLineTimeStamp = header[6]
        frameTimeDelta = thisLineTimeStamp - lastLineTimestamp
        #print("Packet: ", header[4], "frameID:", header[7], "timestamp:", header[6], "Delta:", frameTimeDelta)
        lastLineTimestamp = thisLineTimeStamp

        if line[5:6] == b'\x02':
            header = struct.unpack('<HBBBBQfIBB', line[0:24])
            frameID = header[7]
            
            # Bytes
            byteCode = '<'
            for x in range(22):
                byteCode = byteCode + 'IIHHfffBBBBBBBBBBBBBBHHB'
            byteCode = byteCode + 'BB'

            unpacked = struct.unpack(byteCode, line[24:972])

            lapDistance      = unpacked[(carOfInterest * 24) + 4]
            currentLapTimeMS = unpacked[(carOfInterest * 24) + 1]
            distanceTrace.append([frameID, lapDistance])
            lapTimeTrace.append([frameID, currentLapTimeMS])
        #elif message[5:6] == b'\x03':
        #    messageBuffer.append(message)
        #elif message[5:6] == b'\x04':
        #    messageBuffer.append(message)
        #elif message[5:6] == b'\x05':
        #    messageBuffer.append(message)
        if line[5:6] == b'\x06':
            header = struct.unpack('<HBBBBQfIBB', line[0:24])
            frameID = header[7]
            
            # Bytes
            byteCode = '<'
            for x in range(22):
                byteCode = byteCode + 'HfffBbHBBHHHHHBBBBBBBBHffffBBBB'
            byteCode = byteCode + 'BBb'

            unpacked = struct.unpack(byteCode, line[24:1347])
            
            speed         = unpacked[(carOfInterest * 16) + 0]
            throttle      = unpacked[(carOfInterest * 16) + 1]
            brake         = unpacked[(carOfInterest * 16) + 3]
            gear          = unpacked[(carOfInterest * 16) + 5]

            speedTrace.append([frameID, speed])
            throttleTrace.append([frameID, throttle])
            brakeTrace.append([frameID, brake])
            gearTrace.append([frameID, gear])
    
        #elif message[5:6] == b'\x07':
        #    messageBuffer.append(message)
        #elif message[5:6] == b'\x08':
        #    messageBuffer.append(message)
        #elif message[5:6] == b'\x09':
        #    messageBuffer.append(message)
        #elif message[5:6] == b'\n':
        #    messageBuffer.append(message)
        #elif message[5:6] == b'\x0b':
        #    messageBuffer.append(message)
    
    
    
    lineCount = lineCount + 1

print("    Data extracted, now start filtering...")

# Check all same length with luck!
print("    Distance trace:", len(distanceTrace))
print("    LapTime  trace:",len(lapTimeTrace))
print("    Speed    trace:",len(speedTrace))
print("    Throrrle trace:",len(throttleTrace))
print("    Brake    trace:",len(brakeTrace))
print("    Gear     trace:",len(gearTrace))

mapFrameToDistance = False

if len(distanceTrace) == len(lapTimeTrace) and len(distanceTrace) == len(speedTrace) and len(distanceTrace) == len(throttleTrace) and len(distanceTrace) == len(brakeTrace) and len(distanceTrace) == len(gearTrace):
    print("    Arrays all same size, no need to map frame to lap distance")
else:
    print("    Arrays have different sizes, will now map frame to lap distance...")
    mapFrameToDistance = True

# Mapping
#for i in range(len(distanceTrace)):
#    print(distanceTrace[i], speedTrace[i])

filterStep1 = []

# Convert all to by distance, this is easy if all the same, no data checking, warning... not robust
if mapFrameToDistance is False:
    for i in range(len(distanceTrace)):
        filterStep1.append([distanceTrace[i][1], lapTimeTrace[i][1], speedTrace[i][1], throttleTrace[i][1], brakeTrace[i][1],  gearTrace[i][1]])
        #lapTimeTrace[i][0]  = distanceTrace[i][1]
        #speedTrace[i][0]    = distanceTrace[i][1]
        #throttleTrace[i][0] = distanceTrace[i][1]
        #brakeTrace[i][0]    = distanceTrace[i][1]
        #gearTrace[i][0]     = distanceTrace[i][1]
# Mapping
else:
    for i in range(len(distanceTrace)):
        frameID = distanceTrace[i][0]
        #Get lapTime
        lapTimeAtThisFrame = None
        for item in lapTimeTrace:
            if item[0] == frameID:
                lapTimeAtThisFrame = item[1]
                #print(frameID, lapTimeAtThisFrame)
                break
        #Get speed
        speedAtThisFrame = None
        for item in speedTrace:
            if item[0] == frameID:
                speedAtThisFrame = item[1]
                #print(frameID, speedAtThisFrame)
                break
        #Get throttle
        throttleAtThisFrame = None
        for item in throttleTrace:
            if item[0] == frameID:
                throttleAtThisFrame = item[1]
                #print(frameID, throttleAtThisFrame)
                break
        #Get brake
        brakeAtThisFrame = None
        for item in brakeTrace:
            if item[0] == frameID:
                brakeAtThisFrame = item[1]
                #print(frameID, brakeAtThisFrame)
                break
        #Get gear
        gearAtThisFrame = None
        for item in gearTrace:
            if item[0] == frameID:
                gearAtThisFrame = item[1]
                #print(frameID, gearAtThisFrame)
                break
        filterStep1.append([distanceTrace[i][1], lapTimeAtThisFrame, speedAtThisFrame, throttleAtThisFrame, brakeAtThisFrame,  gearAtThisFrame])




#for item in filterStep1:
#    print(item)

#Filter by positive distance and positive lap time, (works only for hot laps)
filterStep2 = []
for item in filterStep1:
    if item[0] >= 0.0 and item[1] >= 0.0:
        filterStep2.append(item)

#for item in filterStep2:
#    print(item)

# Filter for the desired lap, by checking when the lap distance and lap time restart
lapCount = 0
filterStep3 = []
previousItem = None

for item in filterStep2:
    if previousItem is None:
        previousItem = item[:]
        #copy and append
        newItem = item[:]
        newItem.append(lapCount)
        filterStep3.append(newItem)
        continue
    else:
        if item[0] <= previousItem[0] and item[1] <= previousItem[1]:
            print("Lap Count")
            lapCount = lapCount + 1

            
        previousItem = item[:]
        #copy and append
        newItem = item[:]
        newItem.append(lapCount)
        filterStep3.append(newItem)

# Check order of data
#for item in filterStep3:
#    print(item)

# Jimmy rig clearing an erroneous point
filterStep3.pop(0)




#Desktop
#plotwidth = 1200
#Mobile
plotwidth = 800
plotheight = 400
lineThickness = 3.0
fontSize = 24
totalLapDistanceMeters = 5276

traceFileData = {}

## Speed
xData = []
yData = []
secondLastDatumValue = None
lastDatumValue = None
for item in filterStep3:
    if item[6] == lapOfInterest:
        #Set the first two loops
        if secondLastDatumValue is None:
            xData.append(item[0])
            yData.append(item[2])
            secondLastDatumValue = item[2]
            continue
        if lastDatumValue is None:
            xData.append(item[0])
            yData.append(item[2])
            lastDatumValue = item[2]
            continue

        if lastDatumValue == item[2] and secondLastDatumValue == item[2]:
            xData[len(xData)-1] = item[0]
            yData[len(yData)-1] = item[2]
            secondLastDatumValue = yData[len(yData)-2]
            lastDatumValue = yData[len(yData)-1]

        else:
            xData.append(item[0])
            yData.append(item[2])

            secondLastDatumValue = yData[len(yData)-2]
            lastDatumValue = yData[len(yData)-1]


# Clean erroneous items out of data
#for item in filterStep3:
#    print(item)


#for i in range(len(xData)):
#    print(xData[i], "," , yData[i])
    
data = {'Lap Distance': xData, 'Speed' : yData}
df = pd.DataFrame(data)

traceFileData['Speed'] = {'Lap Distance': xData, 'Speed' : yData}

#Red Bull Yellow 252 / 215 / 0   "#FCD700"
# Red Bull dark blue 0 / 26 / 48
# Red Bull red 237 / 24 / 71 #ED1847
# Red Bull pink 167/169/ 172
# Red Bull blue 47 75 154 #2F4B9A


fig1 = px.line(df, df['Lap Distance'], df['Speed'], title="Max Speed Trace",width=plotwidth, height=plotheight)
fig1.update_traces(line=dict(color="#FCD700", width=lineThickness))
fig1.update_layout(
    #paper_bgcolor="black", #'rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font = dict(color = 'white',size = fontSize),
    uniformtext_minsize=24,
    xaxis_range=[-1,totalLapDistanceMeters],
    yaxis_range=[-1,350]
)
fig1.update_xaxes(tick0=0.0, dtick = 500,showgrid=True, gridcolor ='rgba(255,255,255,0.5)', gridwidth=0.5)
fig1.update_yaxes(tick0=0.0, dtick = 50,showgrid=True, gridcolor ='rgba(255,255,255,0.5)', gridwidth=0.5,zeroline=False, zerolinewidth= 0.0, zerolinecolor='rgba(0,0,0,0.0)')
#fig1.show()

if not os.path.exists(outputDir):
    os.mkdir(outputDir)

#fig1.write_image(outputDir + "/max1.png")

## Throttle
xData = []
yData = []
secondLastDatumValue = None
lastDatumValue = None
for item in filterStep3:
    if item[6] == lapOfInterest:
        #Set the first two loops
        if secondLastDatumValue is None:
            xData.append(item[0])
            yData.append(item[3])
            secondLastDatumValue = item[3]
            continue
        if lastDatumValue is None:
            xData.append(item[0])
            yData.append(item[3])
            lastDatumValue = item[3]
            continue

        if lastDatumValue == item[3] and secondLastDatumValue == item[3]:
            xData[len(xData)-1] = item[0]
            yData[len(yData)-1] = item[3]
            secondLastDatumValue = yData[len(yData)-2]
            lastDatumValue = yData[len(yData)-1]

        else:
            xData.append(item[0])
            yData.append(item[3])

            secondLastDatumValue = yData[len(yData)-2]
            lastDatumValue = yData[len(yData)-1]

#for i in range(len(xData)):
#    print(xData[i], "," , yData[i])

data = {'Lap Distance': xData, 'Throttle' : yData}
df = pd.DataFrame(data)

traceFileData['Throttle'] = {'Lap Distance': xData, 'Throttle' : yData}

fig2 = px.line(df, df['Lap Distance'], df['Throttle'], title="Max Throttle Trace",width=plotwidth, height=plotheight)
fig2.update_traces(line=dict(color="#A7A9AC", width=lineThickness))
fig2.update_layout(
    #paper_bgcolor="black", #'rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font = dict(color = 'white',size = fontSize),
    uniformtext_minsize=24,
    xaxis_range=[-1,totalLapDistanceMeters],
    yaxis_range=[-.25,1.25]
)
fig2.update_xaxes(tick0=0.0, dtick = 500,showgrid=True, gridcolor ='rgba(255,255,255,0.5)', gridwidth=0.5)
fig2.update_yaxes(tick0=0.0, dtick = 0.5, showgrid=True, gridcolor ='rgba(255,255,255,0.5)', gridwidth=0.5, zeroline=False, zerolinewidth= 0.0, zerolinecolor='rgba(0,0,0,0.0)')
#fig2.show()

if not os.path.exists(outputDir):
    os.mkdir(outputDir)

#fig2.write_image(outputDir + "/max2.png")

## Brake
xData = []
yData = []
secondLastDatumValue = None
lastDatumValue = None
for item in filterStep3:
    if item[6] == lapOfInterest:
        #Set the first two loops
        if secondLastDatumValue is None:
            xData.append(item[0])
            yData.append(item[4])
            secondLastDatumValue = item[4]
            continue
        if lastDatumValue is None:
            xData.append(item[0])
            yData.append(item[4])
            lastDatumValue = item[4]
            continue

        if lastDatumValue == item[4] and secondLastDatumValue == item[4]:
            xData[len(xData)-1] = item[0]
            yData[len(yData)-1] = item[4]
            secondLastDatumValue = yData[len(yData)-2]
            lastDatumValue = yData[len(yData)-1]

        else:
            xData.append(item[0])
            yData.append(item[4])

            secondLastDatumValue = yData[len(yData)-2]
            lastDatumValue = yData[len(yData)-1]


#for i in range(len(xData)):
#    print(xData[i], "," , yData[i])
    
data = {'Lap Distance': xData, 'Brake' : yData}
df = pd.DataFrame(data)

traceFileData['Brake'] = {'Lap Distance': xData, 'Brake' : yData}

fig3 = px.line(df, df['Lap Distance'], df['Brake'], title="Max Brake Trace",width=plotwidth, height=plotheight)
fig3.update_traces(line=dict(color="#ED1847", width=lineThickness))
fig3.update_layout(
    #paper_bgcolor="black", #'rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font = dict(color = 'white',size = fontSize),
    uniformtext_minsize=24,
    xaxis_range=[-1,totalLapDistanceMeters],
    yaxis_range=[-.25,1.25]
)
fig3.update_xaxes(tick0=0.0, dtick = 500, showgrid=True, gridcolor ='rgba(255,255,255,0.5)', gridwidth=0.5)
fig3.update_yaxes(tick0=0.0, dtick = .5, showgrid=True, gridcolor ='rgba(255,255,255,0.5)', gridwidth=0.5, zeroline=False, zerolinewidth= 0.0, zerolinecolor='rgba(0,0,0,0.0)')
#fig3.show()
if not os.path.exists(outputDir):
    os.mkdir(outputDir)

#fig3.write_image(outputDir + "/max3.png")

## Gear
xData = []
yData = []
secondLastDatumValue = None
lastDatumValue = None
for item in filterStep3:
    if item[6] == lapOfInterest:
        #Set the first two loops
        if secondLastDatumValue is None:
            xData.append(item[0])
            yData.append(item[5])
            secondLastDatumValue = item[5]
            continue
        if lastDatumValue is None:
            xData.append(item[0])
            yData.append(item[5])
            lastDatumValue = item[5]
            continue

        if lastDatumValue == item[5] and secondLastDatumValue == item[5]:
            xData[len(xData)-1] = item[0]
            yData[len(yData)-1] = item[5]
            secondLastDatumValue = yData[len(yData)-2]
            lastDatumValue = yData[len(yData)-1]
            

        else:
            xData.append(item[0])
            yData.append(item[5])

            secondLastDatumValue = yData[len(yData)-2]
            lastDatumValue = yData[len(yData)-1]


#for i in range(len(xData)):
#    print(xData[i], "," , yData[i])


data = {'Lap Distance': xData, 'Gear' : yData}
df = pd.DataFrame(data)

traceFileData['Gear'] = {'Lap Distance': xData, 'Gear' : yData}

fig4 = px.line(df, df['Lap Distance'], df['Gear'], title="Max Gear Trace",width=plotwidth, height=plotheight)
fig4.update_traces(line=dict(color="#2F4B9A", width=lineThickness))
fig4.update_layout(
    #paper_bgcolor="black", #'rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font = dict(color = 'white', size = fontSize),
    uniformtext_minsize=24,
    xaxis_range=[-1,totalLapDistanceMeters],
    yaxis_range=[-.1,9]
)
fig4.update_xaxes(tick0=0.0, dtick = 500, showgrid=True, gridcolor ='rgba(255,255,255,0.5)', gridwidth=0.5)
fig4.update_yaxes(tick0=0.0, dtick = 1, showgrid=True, gridcolor ='rgba(255,255,255,0.5)', gridwidth=0.5)
#fig4.show()

if not os.path.exists(outputDir):
    os.mkdir(outputDir)

#fig4.write_image(outputDir + "/max4.png")

fig1Traces = []
fig2Traces = []
fig3Traces = []
fig4Traces = []

for trace in range(len(fig1["data"])):
    fig1Traces.append(fig1["data"][trace])
for trace in range(len(fig2["data"])):
    fig2Traces.append(fig2["data"][trace])
for trace in range(len(fig3["data"])):
    fig3Traces.append(fig3["data"][trace])
for trace in range(len(fig4["data"])):
    fig4Traces.append(fig4["data"][trace])


stackfig = make_subplots(rows=4, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.00)

stackfig.add_trace(fig1Traces[0],
              row=1, col=1)

stackfig.add_trace(fig2Traces[0],
              row=2, col=1)

stackfig.add_trace(fig3Traces[0],
              row=3, col=1)

stackfig.add_trace(fig4Traces[0],
              row=4, col=1)

stackfig.update_layout(#height=plotheight*4, width=plotwidth,
                  title_text="Max Saudi")

stackfig.update_layout(
    #paper_bgcolor="black", #'rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font = dict(color = 'white',size = fontSize),
    uniformtext_minsize=24,
    xaxis_range=[-1,totalLapDistanceMeters],
    images=[dict(
        source="Powered_By_Oracle_Cloud_Logo_RGB_White-01.png",
        xref="paper", yref="paper",
        x=1, y=1.05,
        sizex=0.2, sizey=0.2,
        xanchor="right", yanchor="bottom"
      )]
)

stackfig.update_xaxes(title_text="Lap Distance", tick0=0.0,  dtick = 500,showgrid=True, gridcolor ='rgba(255,255,255,0.5)', gridwidth=0.5)
stackfig.update_yaxes(row=1,col=1, title_text="Speed", range=[-1,350], tick0=0.0, dtick = 50,showgrid=True, gridcolor ='rgba(255,255,255,0.5)', gridwidth=0.5, zeroline=False, zerolinewidth= 0.0, zerolinecolor='rgba(0,0,0,0.0)')
stackfig.update_yaxes(row=2,col=1, title_text="Throttle", range=[-.25,1.25], tick0=0.0, dtick = 0.5, showgrid=True, gridcolor ='rgba(255,255,255,0.5)', gridwidth=0.5, zeroline=False, zerolinewidth= 0.0, zerolinecolor='rgba(0,0,0,0.0)')
stackfig.update_yaxes(row=3,col=1, title_text="Brake", range=[-.25,1.25], tick0=0.0, dtick = .5, showgrid=True, gridcolor ='rgba(255,255,255,0.5)', gridwidth=0.5, zeroline=False, zerolinewidth= 0.0, zerolinecolor='rgba(0,0,0,0.0)')
stackfig.update_yaxes(row=4,col=1, title_text="Gear", range=[-.1,9], tick0=0.0, dtick = 1, showgrid=True, gridcolor ='rgba(255,255,255,0.5)', gridwidth=0.5)


stackfig.show()

if not os.path.exists(outputDir):
    os.mkdir(outputDir)

#stackfig.write_image(outputDir + "/maxStacked.png")
stackfig.write_html(outputDir + "/maxStacked.html")

if traces:
    f = open(outputDir + "/traces.csv", "w")

    f.write("Speed")
    f.write('\n')

    f.write("LapDistance,Speed")
    f.write('\n')

    for i in range(len(traceFileData['Speed']['Speed'])):
        f.write(str(traceFileData['Speed']['Lap Distance'][i]) + "," + str(traceFileData['Speed']['Speed'][i]))
        f.write('\n')
    

    f.write("Throttle")
    f.write('\n')

    f.write("LapDistance,Throttle")
    f.write('\n')

    for i in range(len(traceFileData['Throttle']['Throttle'])):
        f.write(str(traceFileData['Throttle']['Lap Distance'][i]) + "," + str(traceFileData['Throttle']['Throttle'][i]))
        f.write('\n')
    

    f.write("Brake")
    f.write('\n')

    f.write("LapDistance,Brake")
    f.write('\n')

    for i in range(len(traceFileData['Brake']['Brake'])):
        f.write(str(traceFileData['Brake']['Lap Distance'][i]) + "," + str(traceFileData['Brake']['Brake'][i]))
        f.write('\n')

    f.write("Gear")
    f.write('\n')

    f.write("LapDistance,Gear")
    f.write('\n')

    for i in range(len(traceFileData['Gear']['Gear'])):
        f.write(str(traceFileData['Gear']['Lap Distance'][i]) + "," + str(traceFileData['Gear']['Gear'][i]))
        f.write('\n')

    f.close()
    #print(traceFileData)