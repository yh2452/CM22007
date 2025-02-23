import sqlite3
import datetime

'''
USER DATABASE
--> access socials a user has attended in the past
    --> mark events as 'attended' once the event date has passed
    --> Calendar for future events user is planning to attend
--> access socials a user is planning to attend
    --> mark events accordingly when users first select to 'attend' (similar for 'unattend')
--> access events users have previously pinned
    --> mark events as 'pinned' for users
--> access followed societies
    --> mark societies as 'followed' when users first select to 'follow' (similar for 'unfollow')
'''

### [ATTENDED TABLE] ###
# An 'Attended' Table where we store (userID, eventID)

def toggleAttend(cursor, userID, eventID):
    """
    Allows a user to mark or unmark an event for future attending.
    """
    cursor.execute("SELECT eventID FROM Attended WHERE userID = (?) AND eventID = (?)", (userID, eventID))
    event = cursor.fetchall()
    if not event:
        cursor.execute("INSERT INTO Attended VALUES (?,?)",(userID, eventID))
    else:
        cursor.execute("DELETE FROM Attended WHERE userID = (?) AND eventID = (?)", (userID, eventID))

def getAttendedEvents(cursor, userID, flag):
    """
    Return all socials the user has attended in the past, or ones they are planning to attend.

    flag: TRUE = past attended events, FALSE = future events they plan to attend
    """
    date = datetime.datetime.now()
    
    if flag:
        cursor.execute("SELECT Event.* FROM Event INNER JOIN Attended ON Event.eventID=Attended.eventID WHERE Attended.userID = (?) AND Event.date < (?)", (userID, date))
    else:
        cursor.execute("SELECT Event.* FROM Event INNER JOIN Attended ON Event.eventID=Attended.eventID WHERE Attended.userID = (?) AND Event.date >= (?)", (userID, date))

    return cursor.fetchall()  # any result formatting?

### [PINNED TABLE] ###
# A 'Pinned' Table where we store (userID, eventID)

def togglePin(cursor, userID, eventID):
    """
    Allows a user to pin or unpin an event.
    """
    cursor.execute("SELECT eventID FROM Pinned WHERE userID = (?) AND eventID = (?)", (userID, eventID))
    event = cursor.fetchall()
    if not event:
        cursor.execute("INSERT INTO Pinned VALUES (?,?)", (userID, eventID))
    else:
        cursor.execute("DELETE FROM Pinned WHERE userID = (?) AND eventID = (?)", (userID, eventID))

def getPinnedEvents(cursor, userID):
    """
    Returns all events the user has pinned.
    """
    cursor.execute("SELECT Event.* FROM Event INNER JOIN Pinned ON Event.eventID=Pinned.eventID WHERE Attended.userID = (?)", (userID,)) 
    return cursor.fetchall()  # any result formatting?

### [FOLLOWED TABLE] ###
# A 'Followed' Table where we store (userID, societyID)

def toggleFollow(cursor, userID, socID):
    """
    Allows a user to follow or unfollow a society.
    """
    cursor.execute("SELECT societyID FROM Followed WHERE userID = (?) AND societyID (?)", (userID, socID))
    soc = cursor.fetchall()
    if not soc:
        cursor.execute("INSERT INTO Followed VALUES (?,?)", (userID, socID))
    else:
        cursor.execute("DELETE FROM Followed WHERE userID = (?) AND societyID (?)", (userID, socID))

def getFollowed(cursor, userID):
    """
    Returns all societies the user follows.
    """
    cursor.execute("SELECT Society.* FROM Society INNER JOIN Followed ON Society.societyID=FOLLOWED.societyID WHERE Followed.userID = (?)", (userID,))
    return cursor.fetchall()  # any result formatting?

'''
SOCIAL DATABASE
(*) Seems like we are pulling the society info directly from the SU website? How do we do that
--> access social/event info (listed in acceptance test 2.1)
    --> creation of socials by users/committee members
--> Apply search filters and return corresponding results (special case: no results)
--> access engagement metrics (no. of people interested, how many turned up for previous socials, etc.?)
'''

'''
FEEDBACK DATABASE
--> access user ratings and feedback for a specific social
    --> generate an entry for each social once the event date has passed 
        --> maybe let event hoster input how many people showed up (for engagement metrics?)
    --> add user ratings and feedback to the specific social in the first place
--> access malpractice reports (via reportID or eventID)
    --> add malpractice reports to database in the first place
'''

### [FEEDBACK TABLE] ###
# A 'Feedback' Table where we store (feedbackID, eventID, feedbackData?)

def addFeedback(cursor, feedbackData):
    """
    Adds user feedback to the corresponding table.
    """
    # format feedback data?
    # feedbackData = format(feedbackData)
    nextID = 1  # how are we going to keep track of next available ID?
    nextID += 1 
    cursor.execute("INSERT INTO Feedback VALUES (?, ?)", (nextID, feedbackData))

def getFeedback(cursor, feedbackID):
    """
    Retrieves feedback data for a given feedbackID.
    """
    cursor.execute("SELECT feedbackData FROM Feedback WHERE feedbackID == (?)", (feedbackID,))
    return cursor.fetchall()  # any result formatting?

def getEventFeedback(cursor, eventID):
    """
    Retrieves all feedback for a given event.
    """
    cursor.execute("SELECT feedbackData FROM Feedback WHERE eventID == (?)", (eventID,))
    return cursor.fetchall()  # any result formatting?


### [REPORT TABLE] ###
# A 'Report' Table where we store (reportID, eventID, reportData?)

def addReport(cursor, reportData):
    """
    Adds a malpractice report to the corresponding table.
    """
    # format report data?
    # reportData = format(reportData)
    nextID = 1  # how are we going to keep track of next available ID? 
    cursor.execute("INSERT INTO Feedback VALUES (?, ?)", (nextID, reportData))

def getReport(cursor, reportID):
    """
    Retrieves report data for a given reportID.
    """
    cursor.execute("SELECT reportData FROM Report WHERE reportID == (?)", (reportID,))
    return cursor.fetchall()  # any result formatting?

def getEventReports(cursor, eventID):
    """
    Retrieves all reports for a given event.
    """
    cursor.execute("SELECT reportData FROM Report WHERE eventID == (?)", (eventID,))
    return cursor.fetchall()  # any result formatting?
