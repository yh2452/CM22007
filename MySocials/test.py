import sqlite3

connection = sqlite3.connect("MySocials/table.db")
cursor = connection.cursor()
cursor.row_factory = sqlite3.Row
cursor.execute("SELECT * FROM Society")
values = cursor.fetchall()
for value in values:
    print(value["societyID"])
