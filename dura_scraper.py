import requests
import re
import mysql.connector
import datetime
import sched, time

SUCCESS_CODE = 200
URL = "https://game-website.com/statuscheck.php"
URL = "https://dura-online.com/statuscheck.php"
lastEventCompleted = 1
websiteFailCount = 0

schedule = sched.scheduler(time.time, time.sleep)

def scrapeDura(sc): 
	global lastEventCompleted
	global websiteFailCount
	currentDateTime = datetime.datetime.now()

	if websiteFailCount > 5:
		websiteFailCount = 5

	if lastEventCompleted:
		lastEventCompleted = 0

		page = requests.get(URL)
		if page.status_code == SUCCESS_CODE:

			#Format: "Name: Erin, level: 87"
			onlinePlayers = re.findall("Name: ([a-zA-Z -]+)+,", page.text)
			onlinePlayersLevels = re.findall(", level: ([0-9]+)", page.text)

			if onlinePlayers and onlinePlayersLevels:
				websiteFailCount = 0
				schedule.enter(180, 1, scrapeDura, (sc,))
				amountOnlinePlayers = len(onlinePlayers)
				print(amountOnlinePlayers,"Players Online")

				mydb = mysql.connector.connect(
				  host="localhost",
				  user="root",
				  password="root",
				  database="dura_alt_finder"
				)

				mycursor = mydb.cursor()

				sql = "INSERT INTO online_entry (id, date) VALUES (%s, %s)"
				val = (None, currentDateTime)
				mycursor.execute(sql, val)

				mydb.commit()

				currentPlayerIndex = 0 
				while currentPlayerIndex < amountOnlinePlayers:
					playerName = onlinePlayers[currentPlayerIndex]
					onlinePlayers[currentPlayerIndex] = [playerName, mycursor.lastrowid, onlinePlayersLevels[currentPlayerIndex]]
					currentPlayerIndex += 1

				sql = "INSERT INTO online_entry_player (player_name, online_entry_id, player_level) VALUES (%s, %s, %s)"

				mycursor.executemany(sql, onlinePlayers)

				mydb.commit()

				print(str(currentDateTime) + ": Database Updated")
			else:
				schedule.enter(30 + (websiteFailCount * 30), 1, scrapeDura, (sc,))
				websiteFailCount += 1
				print(str(currentDateTime) + ": No players online.")
		else:
			schedule.enter(30 + (websiteFailCount * 30), 1, scrapeDura, (sc,))
			websiteFailCount += 1
			print(str(currentDateTime) + " Error: Could not reach website.")

		lastEventCompleted = 1
	else:
		print(str(currentDateTime) + " Error: Previous event not completed. Hung Somehow")


schedule.enter(1, 1, scrapeDura, (schedule,))
schedule.run()
