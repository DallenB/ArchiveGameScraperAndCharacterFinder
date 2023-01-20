
import mysql.connector
import datetime
import time
import collections

# Entry only valid if login/logout with 5 minutes
# Return amount of tries
# Return whether on same account, both logged in at same time

# Find Player

# foreach login entry

# otherPlayers[playerName
#     differentAccount = [false|true],
#     loginSwitchTimes = 0
# ]

# if player is online
#     if player was NOT online in last entry
#         search last entry for chars that logged out
#     if player was online
#         nothing

# if player is offline
#     if player was online in last entry
#         search next entry for chars that logged in
#     if player was offline
#         nothing

onlineEntryMaximumValiditySeconds = 300 #5 Minute(s)
onlineEntryMinimumValiditySeconds = 60 #1 Minute(s)
suspiciousPlayers = {}
def secondsBetweenTimestamps(timeA, timeB):
    return timeA.timestamp() - timeB.timestamp()

def isValidTimestampDifference(timeA,timeB):
    difference = secondsBetweenTimestamps(timeA, timeB)
    return difference <= onlineEntryMaximumValiditySeconds and difference >= onlineEntryMinimumValiditySeconds

def addSuspicion(name):
    global suspiciousPlayers
    
    #first time player
    if not name in suspiciousPlayers:
        suspiciousPlayers[name] = 1
    elif suspiciousPlayers[name] != -1:
        suspiciousPlayers[name] += 1

def sortSuspicionListByCount():
    global suspiciousPlayers
    suspiciousPlayers = sorted(suspiciousPlayers.items(), key=lambda x: x[1], reverse=True)

def printTopSuspicionList(amountToDisplay):
    global suspiciousPlayers
    amountSuspiciousPlayers = len(suspiciousPlayers)
    i = 0
    displayString = "Likely Alt Chars: "
    while i < amountToDisplay and i < amountSuspiciousPlayers:
        if i == 0:
            displayString = displayString + str(suspiciousPlayers[i][0]) + " [" + str(suspiciousPlayers[i][1]) + "]"
        elif suspiciousPlayers[i][1] != -1:
            displayString = displayString + ", " + str(suspiciousPlayers[i][0]) + " [" + str(suspiciousPlayers[i][1]) + "]"
        i += 1
    print(displayString)


def findAltsForCharacter(playerName, onlySameAccount):
    global suspiciousPlayers
    sql = "SELECT `online_entry_player`.`player_name`, `online_entry_player`.`online_entry_id`, `online_entry`.`date` FROM `online_entry_player` INNER JOIN `online_entry` ON online_entry.id = online_entry_player.online_entry_id WHERE `player_name` LIKE '" + playerName + "' ORDER BY `online_entry_id` ASC"

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="dura_alt_finder"
    )

    ##Get loginEntry
    mycursor = mydb.cursor()

    mycursor.execute(sql)

    playerEntryResult = mycursor.fetchall()
    print("Multi-Client Results:", "Hidden" if onlySameAccount else "Included", "\n" + playerName + "'s player entries: " + str(len(playerEntryResult)))

    wasOnline = False
    lastEntryTimestamp = False
    lastEntryID = False
    previousPlayerEntryID = False

    #for each login entry
    playerEntryIndex = 0 
    amountPlayerEntries = len(playerEntryResult)
    while playerEntryIndex < amountPlayerEntries:
        #make sure we have a valid previous entry
        #get the online_players datetime from the last check
        if playerEntryResult[playerEntryIndex][1]-1 >= 0:
            sql = "SELECT * FROM `online_entry` WHERE `id` = "+str(playerEntryResult[playerEntryIndex][1]-1)
            mycursor.execute(sql)
            lastEntryResult = mycursor.fetchall()
            if lastEntryResult:
                lastEntryID = lastEntryResult[0][0]
                lastEntryTimestamp = lastEntryResult[0][1]

        #Check if we were online in previous event
        if playerEntryResult[playerEntryIndex][1] == previousPlayerEntryID + 1:
            wasOnline = True
        else:
            wasOnline = False

        if previousPlayerEntryID and lastEntryTimestamp and isValidTimestampDifference(playerEntryResult[playerEntryIndex][2], lastEntryTimestamp):
            #If they just logged in
            if not wasOnline:
                #Check for players that logged out
                #Get all players from lastEntryID
                sql = "SELECT `player_name` FROM `online_entry_player` WHERE `online_entry_id` ="+str(lastEntryID)
                mycursor.execute(sql)
                oldPlayers = mycursor.fetchall()

                #Get all players from current entryID
                sql = "SELECT `player_name` FROM `online_entry_player` WHERE `online_entry_id` ="+str(playerEntryResult[playerEntryIndex][1])
                mycursor.execute(sql)
                currentPlayers = mycursor.fetchall()

                #for each player that was logged in earlier
                for oldPlayer in oldPlayers:
                    playerFound = False
                    #for each currentPlayer in currentPlayers
                    for currentPlayer in currentPlayers:
                        #Find players that logged out
                        
                        if oldPlayer[0] == currentPlayer[0]:
                            playerFound = True
                            break

                    if not playerFound:
                        addSuspicion(oldPlayer[0])
                    elif onlySameAccount:
                        suspiciousPlayers[oldPlayer[0]] = -1




        #Check the next event to see if this character logs out
        #If not last index in array AND Next player Enter Index ID != current index + 1
        if (not playerEntryIndex + 1 >= amountPlayerEntries) and playerEntryResult[playerEntryIndex+1][1] != playerEntryResult[playerEntryIndex][1] + 1:
            #print("Character logs out")
            sql = "SELECT `player_name` FROM `online_entry_player` WHERE `online_entry_id` ="+str(playerEntryResult[playerEntryIndex][1] + 1)
            mycursor.execute(sql)
            nextPlayers = mycursor.fetchall()

            #Get all players from current entryID
            sql = "SELECT `player_name` FROM `online_entry_player` WHERE `online_entry_id` ="+str(playerEntryResult[playerEntryIndex][1])
            mycursor.execute(sql)
            currentPlayers = mycursor.fetchall()

            #for each player online next
            for nextPlayer in nextPlayers:
                playerFound = False
                #for each currentPlayer in currentPlayers
                for currentPlayer in currentPlayers:
                    #Find players that logged in
                    if nextPlayer[0] == currentPlayer[0]:
                        playerFound = True
                        break

                #If player was NOT online before
                if not playerFound:
                    addSuspicion(nextPlayer[0])
                elif onlySameAccount:
                    suspiciousPlayers[nextPlayer[0]] = -1

        lastEntryTimestamp = False
        previousPlayerEntryID = playerEntryResult[playerEntryIndex][1]
        playerEntryIndex += 1

    sortSuspicionListByCount()


findAltsForCharacter("Akallabeth", True)
printTopSuspicionList(10)