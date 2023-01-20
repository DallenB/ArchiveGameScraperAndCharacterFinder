
import mysql.connector
import datetime
import time
import collections
import re

#Usage:
#User inputs last X days
#User inputs top X number of players to return
#User recieves list of players and Hours played

#Timeperiod - 1 day = 24hrs
#Counting method
    #Each onlineEntry must be within 5 minutes of next to be considered valid
    #exact seconds added from minutes between timestamps

#Works
#Time to check X = current time - Days to search
#Skip records until we find first entry for X time
#Go until end

onlineEntryMaximumValiditySeconds = 300 #5 Minute(s)

#playerTimes["Jerry"] = SECONDS
playerTimes = {}
amountTimeSearched = 0

def sortListPlayerTimesByCount():
    global playerTimes
    playerTimes = sorted(playerTimes.items(), key=lambda x: x[1], reverse=True)

def printTopPlayerTimesList(amountToDisplay):
    global playerTimes
    amountPlayers = len(playerTimes)
    i = 0

    displayString = "Total Possible Time Recorded - " + str(datetime.timedelta(seconds=int(amountTimeSearched))) + "\n"

    while i < amountToDisplay and i < amountPlayers:

        sec = datetime.timedelta(seconds=int(playerTimes[i][1]))
        d = datetime.datetime(1,1,1) + sec

        playerUptime = playerTimes[i][1] / amountTimeSearched * 100
        playerTimePlayed = ""
        if d.day-1 != 0:
            playerTimePlayed = str(d.day-1) + ":" + str(d.hour) + ":" + str(d.minute) + ":" + str(d.second)
        else:
            playerTimePlayed = str(d.hour) + ":" + str(d.minute) + ":" + str(d.second)

        if i == 0:
            displayString = displayString + str(i + 1) + ": " + str(playerTimes[i][0]) + " [" + str(round(playerUptime)) + "% " + str(playerTimePlayed) + "]"
        else:
            displayString = displayString + str(i + 1) + ": " + str(playerTimes[i][0]) + " [" + str(round(playerUptime)) + "% " + str(playerTimePlayed) + "]"
        displayString = displayString + "\n"
        i += 1
    print(displayString)


def findInsomniacs(days, includeGamemasters):
    global amountTimeSearched
    global playerTimes
    secondsLostFromInvalidTimestamps = 0

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="dura_alt_finder"
    )

    ##Get loginEntry
    mycursor = mydb.cursor()

    #Get all loginEntrys DESCENDING BY ID
    sql = "SELECT * FROM `online_entry` ORDER BY `id` ASC"

    mycursor.execute(sql)

    entryResult = mycursor.fetchall()

    currentDateTime = datetime.datetime.now()
    dateTimeSeachUntil = currentDateTime - datetime.timedelta(seconds=60 * 60 * 24 * days)

    entryIndex = len(entryResult) - 1
    #Loop through all entries
    while entryIndex > 0:
        #Check if we have reached our time limit
        entryTimestamp = entryResult[entryIndex][1]
        if entryResult[entryIndex][1] > dateTimeSeachUntil:
            #find seconds from this entry to next
            secondsBetweenEntry = entryResult[entryIndex][1].timestamp() - entryResult[entryIndex-1][1].timestamp()
            #If time difference is smaller than X(5) minutes (possible missing data)
            if secondsBetweenEntry <= onlineEntryMaximumValiditySeconds:
                #Valid, can add time

                #Get all players with this online entry
                sql = "SELECT `player_name` FROM `online_entry_player` WHERE `online_entry_id` ="+str(entryResult[entryIndex][0])
                mycursor.execute(sql)
                entryPlayers = mycursor.fetchall()

                #Add time for all these players
                for player in entryPlayers:
                    #If player is in dictionary
                    if player[0] in playerTimes:
                        playerTimes[player[0]] = playerTimes[player[0]] + secondsBetweenEntry
                    else:
                        staffName = False
                        if not includeGamemasters:
                            staffName = re.search("^(god|admin|gm)", player[0], re.IGNORECASE)
                        if not staffName:
                            playerTimes[player[0]] = secondsBetweenEntry
            else: #invalid entry, reduce total possible time
                secondsLostFromInvalidTimestamps = secondsLostFromInvalidTimestamps + secondsBetweenEntry
        else:
            break

        entryIndex -= 1

    amountTimeSearched = entryResult[len(entryResult) - 1][1].timestamp() - entryResult[entryIndex][1].timestamp() - secondsLostFromInvalidTimestamps
    sortListPlayerTimesByCount()


findInsomniacs(365, False)
printTopPlayerTimesList(300)