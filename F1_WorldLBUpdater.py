# Sends fastest hotlaps per sessionID to Red Bull World Leaderboard Endpoint

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
import requests


import json

# Postgres DB stuff
import psycopg2
from psycopg2 import sql
from config import config

# Postgres get fastest laps
# sessionID, participant
def get_fastest_laps():
    """ get only the fastest laps from unique session ids """
    sql = """SELECT * FROM ( SELECT DISTINCT ON (sessionID) *
                FROM (
                    SELECT *
                    FROM hotlaps
                    ORDER BY laptimeMS ASC) AS FOO
                ORDER BY FOO.sessionID ASC) AS BAR
            ORDER BY BAR.laptimeMS ASC"""
    conn = None
    hotlaps = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql)
        # get the generated id back
        hotlaps = cur.fetchall()
        # commit the changes to the database
        #conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return hotlaps

# Postgres delete laps from live database
# sessionID, lapNumber
def delete_hotlap(tableName, sessionID, lapnumber):
    """ delete a hotlap from the hotlaps table """
    query = sql.SQL("DELETE FROM {table} WHERE (sessionid, lapnumber) IN (( %s, %s ))").format(table=sql.Identifier(tableName))
    
    print("query",query)
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
        cur.execute(query, (sessionID, lapnumber))
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


print("F1_WorldLBUpdater sending data to RedBull endpoints.")

keepGoing = True

while keepGoing:

    fastestlaps = None
    try:
        fastestlaps = get_fastest_laps()
    except:
        print("    Failed to get fastest laps from database.")

    if fastestlaps is not None:
        #Single Message version
        #if len(fastestlaps) > 0:
        if len(fastestlaps) == 1:
            item = fastestlaps[0]
        
            message = json.dumps({
                "playseatPort": str(item[3]),
                "sessionID": str(item[2]),
                "lapNumber": str(item[6]),
                "lapTime": str(item[7]),
                "sectorOne": str(item[8]),
                "sectorTwo": str(item[9]),
                "sectorThree": str(item[10]),
                "isValid": "true"
                })

            print(message)
       

            headers = {
                'Content-Type': 'application/json'
                }

            url = "https://rbr-paddock-pr-299.herokuapp.com/api/telemetry/ingest_playseat_lap"

            response = requests.request("POST", url, headers=headers, data=message)
            
            print("Sent ", len(fastestlaps), " laps to:")
            print("    ", url)
            print(response.text)

            if "leaderboard" in response.text:
                print("    Success!")

                print("        Deleting lap: ", item[2], item[6])
                delete_hotlap("hotlaps", item[2], item[6])




        elif len(fastestlaps) > 1:
        
            # Array of laps
            data = []

            for item in fastestlaps:
                data.append({
                "playseatPort": str(item[3]),
                "sessionID": str(item[2]),
                "lapNumber": str(item[6]),
                "lapTime": str(item[7]),
                "sectorOne": str(item[8]),
                "sectorTwo": str(item[9]),
                "sectorThree": str(item[10]),
                "isValid": "true"
                })
        
            message = json.dumps({"laps":data})

            print(message)

            headers = {
                'Content-Type': 'application/json'
                }

            url = "https://rbr-paddock-pr-299.herokuapp.com/api/telemetry/ingest_playseat_laps"
            response = requests.request("POST", url, headers=headers, data=message)
            
            print("Sent ", len(data), " laps to:")
            print("    ", url)
            
            print(response.text)
            if "leaderboard" in response.text:
                print("    Success!")

                for item in fastestlaps:
                    print("        Deleting lap: ", item[2], item[6])
                    delete_hotlap("hotlaps", item[2], item[6])
        


    time.sleep(3)
    
    
    
    