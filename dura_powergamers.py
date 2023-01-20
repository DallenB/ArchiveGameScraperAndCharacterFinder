
import mysql.connector
import datetime
import time
import collections

#Usage:
#User inputs last X days
#User inputs top X number of players to return
#User recieves list of players and experience gained

#Timeperiod - 1 day = 24hrs
#Counting method
    #exact seconds added from minutes between timestamps

#Works
#Time to check X = current time - Days to search
#Skip records until we find first entry for X time
#Go until end

#playerList["Jerry"] = [startLevel, endLevel]
playerList = {}
playerListExperience = {}


def calculateExpBetweenLevels(startLevel, endLevel):
    return round((((50 * endLevel * endLevel * endLevel) - (150 * endLevel * endLevel) + (400 * endLevel)) / 3) - (((50 * startLevel * startLevel * startLevel) - (150 * startLevel * startLevel) + (400 * startLevel)) / 3))

def sortListplayerListByCount():
    global playerList
    global playerListExperience

    for player in playerList:
        playerListExperience[player] = calculateExpBetweenLevels(playerList[player][0],playerList[player][1])

    playerListExperience = sorted(playerListExperience.items(), key=lambda x: x[1], reverse=True)

def printList(amountToDisplay, days):
    global playerList
    global playerListExperience

    displayString = "Top powergamers within the past " + ("day\n" if days == 1 else (str(days) + " days:\n"))
    playerCount = 1
    for player in playerListExperience:
        if playerCount == 1:
            displayString = displayString + str(playerCount) + ": " + player[0] + " " + str(playerList[player[0]][0]) + ">" + str(playerList[player[0]][1]) + " - " + str(player[1]) + "xp"
        else:
            displayString = displayString + "\n" + str(playerCount) + ": " + player[0] + " " + str(playerList[player[0]][0]) + ">" + str(playerList[player[0]][1]) + " - " + str(player[1]) + "xp"
        playerCount += 1

        if playerCount >= amountToDisplay:
            break

    print(displayString)


def findPowergamers(days):
    global amountTimeSearched
    global playerList

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

    #Start at beginning to end
    loopCount = 0
    amountEntryIndex = len(entryResult)

    # playerList["Alpha"] = [0,0]
    # playerList["Alpha"][0] = 5
    # playerList["Alpha"][1] = 10
    # playerList["Beta"] = [0,0]
    # playerList["Beta"][0] = 2
    # playerList["Beta"][1] = 7
    # playerList["Zeta"] = [0,0]
    # playerList["Zeta"][0] = 5
    # playerList["Zeta"][1] = 3

    #Loop through all entries
    while loopCount < amountEntryIndex:        
        #Check if we have reached our start time
        
        if entryResult[loopCount][1] >= dateTimeSeachUntil:
            #Get all players with this online entry
            sql = "SELECT `player_name`, `player_level` FROM `online_entry_player` WHERE `online_entry_id` ="+str(entryResult[loopCount][0])
            mycursor.execute(sql)
            entryPlayers = mycursor.fetchall()
            print(entryResult[loopCount][1])
            #go through all players online
            for player in entryPlayers:
                if player[1] != 0:
                    #if they are in the list
                    if player[0] in playerList:
                        playerList[player[0]][1] = player[1]
                    #new entry
                    else:
                        #print(player[0])
                        playerList[player[0]] = [0,0]
                        playerList[player[0]][0] = player[1]
                        playerList[player[0]][1] = player[1]
                else:
                    break
        loopCount += 1
    sortListplayerListByCount()
    printList(500, days)

findPowergamers(365)