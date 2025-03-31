import sqlite3

connection = sqlite3.connect("MySocials/table.db")
cursor = connection.cursor()
cursor.execute("INSERT INTO Committee VALUES (?,?,?)", (10, 3, 1))
connection.commit()