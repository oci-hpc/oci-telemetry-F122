import psycopg2
from config import config


def create_tables():
    """ create hotlaps tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE IF NOT EXISTS hotlaps (
            hotlap_id SERIAL PRIMARY KEY,
            timeStamp BIGINT NOT NULL,
            sessionID NUMERIC(25,0) NOT NULL,
            port INTEGER,
            participant VARCHAR(255),
            trackID INTEGER,
            lapNumber INTEGER NOT NULL,
            laptimeMS INTEGER,
            sector1MS INTEGER,
            sector2MS INTEGER,
            sector3MS INTEGER,
            UNIQUE (sessionID, lapNumber)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS hotlaps_archive (
            hotlap_id SERIAL PRIMARY KEY,
            timeStamp BIGINT NOT NULL,
            sessionID NUMERIC(25,0) NOT NULL,
            port INTEGER,
            participant VARCHAR(255),
            trackID INTEGER,
            lapNumber INTEGER NOT NULL,
            laptimeMS INTEGER,
            sector1MS INTEGER,
            sector2MS INTEGER,
            sector3MS INTEGER,
            UNIQUE (sessionID, lapNumber)
        )
        """
        )
    conn = None
    try:
        #print(commands)
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

tables = create_tables()