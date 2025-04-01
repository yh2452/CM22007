import sqlite3

connection = sqlite3.connect("MySocials/table.db")
cursor = connection.cursor()
cursor.row_factory = sqlite3.Row
cursor.execute("SELECT Event.* FROM Event INNER JOIN Attending ON Event.eventID=Attending.eventID WHERE Attending.userID = (?)", (4,))
values = cursor.fetchall()


