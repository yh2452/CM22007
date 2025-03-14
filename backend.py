import sqlite3
import datetime
import hashlib
import os
from profanity_check import predict

def SHA3(data):
    '''
    Hashes a given input (password)
    '''
    salt = os.urandom(16)
    hash_object = hashlib.sha3_256(salt + data)
    return salt.hex() + hash_object.hexdigest()  


def sanitise_input(data, max_length):
    sanitised = data.strip()[:max_length]
    if predict([sanitised]) == 1:
        return None
    return sanitised

'''
USERS
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
        cursor.execute("INSERT INTO Attended VALUES (?,?)", (userID, eventID))
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

### [COMMITTEE TABLE] ###
# A 'Committee' Table where we store (userID, societyID, adminFlag)
# 'admin' is a boolean determining the administrator status of the user within the society.

def addMember(cursor, userID, socID):
    """
    Adds a user as a society committee member.
    """
    cursor.execute("SELECT adminFlag FROM Committee WHERE userID = (?) AND societyID = (?)", (userID, socID))
    status = cursor.fetchall()
    if not status:
        cursor.execute("INSERT INTO Committee VALUES (?,?,?)", (userID, socID, 0))

def removeMember(cursor, userID, socID):
    """
    Removes a user from society committee member status.
    """
    cursor.execute("SELECT adminFlag FROM Committee WHERE userID = (?) AND societyID = (?)", (userID, socID))
    status = cursor.fetchall()
    if not status:
        cursor.execute("DELETE FROM Committee WHERE userID = (?) AND societyID = (?)", (userID, socID))

def toggleAdmin(cursor, userID, socID):
    """
    Sets / unsets a user as a society administrator.
    """
    cursor.execute("SELECT adminFlag FROM Committee WHERE userID = (?) AND societyID = (?)", (userID, socID))
    status = cursor.fetchall()[0][0]
    if status:
        cursor.execute("UPDATE Committee SET adminFlag = 0 WHERE userID = (?) AND societyID = (?)", (userID, socID))
    else:
        cursor.execute("UPDATE Committee SET adminFlag = 1 WHERE userID = (?) AND societyID = (?)", (userID, socID))


'''
SOCIALS
(*) Seems like we are pulling the society info directly from the SU website? How do we do that
--> access social/event info (listed in acceptance test 2.1)
    --> creation of socials by users/committee members
--> Apply search filters and return corresponding results (special case: no results)
--> access engagement metrics (no. of people interested, how many turned up for previous socials, etc.?)
'''

### [SOCIETY TABLE] ###
# A 'Society' table where we store (societyID, societyName)

### [EVENT TABLE] ###
# An 'Event' table where we store (eventID, societyID, userID, eventName, eventDate, eventDescription, eventData, averageRating, ratingCount)
# averageRating is a positive integer between 1 and 5.

def getEventID(cursor, name):
    """
    Obtains the eventID for backend use
    """
    cursor.execute ("SELECT eventID FROM Event WHERE eventName = ?", (name,))
    return cursor.fetchall()

def getSocID(cursor, name):
    """
    Obtains the socID for backend use
    """
    cursor.execute ("SELECT societyID FROM Society WHERE societyName = ?", (name,))
    return cursor.fetchall()

def addSocial (cursor, eventName, societyName, userID, eventDate, eventDescription, eventData):
    """
    Allows a committee member to create a social
    """
    # will also need to take in all the facts about the event as input e.g. the things that you'd filter for
    # does this also need to get added to a society table

    eventID = getEventID(cursor, eventName)
    socID = getSocID(cursor, societyName)
    if eventID is None:
        cursor.execute("INSERT INTO Event (societyID, userID, eventName, eventDate, eventDescription, eventData, averageRating, ratingCount) VALUES (?,?,?,?,?,?,?,?)", (socID, userID, eventName, eventDate, eventDescription, eventData, 0, 0))
        return True
    return False


def deleteSocial(cursor, socID, userID):
    """
    Allows committee members to delete a social
    """
    # this will need to be linked to the whole notification thing
    # what if the comittee member for whatever reason cannot access a device to delete the social, will we need to give other people permissions?
    cursor.execute("DELETE FROM Event WHERE userID = (?) AND societyID = (?)", (userID, socID))
    return

def getSocialData(cursor, socID, eventID, metric):
    """
    Allows data about a social to be found
    """
    #### do we want to show eventDescription (tags) as well? - Jamie
    # what if they type in more than one metric?????????
    # unless we just return all metrics??????? therefore we don't need to take in metric as a parameter
    cursor.execute("SELECT eventData FROM Event WHERE societyID = (?) AND eventID = (?)", (socID, eventID))
    return cursor.fetchall()

def filterSocials (cursor, filters):
    """
    Filters the socials that the user sees
    """
    # I guess filters will be an array? 
    # does this even work???????
    if filters:
        query = "SELECT * FROM Event WHERE "
        keywords = []
        for loop in range (len(filters)):
            if loop == 0:
                query += "eventDescription LIKE (?)"
            else:
                query += " OR eventDescription LIKE (?)"
            keywords.extend([f"%{filters[loop]}%"])
        cursor.execute(query, keywords)
    else:
        cursor.execute("SELECT * FROM Event")
    return cursor.fetchall()


'''
FEEDBACK
--> access user ratings and feedback for a specific social
    --> maybe let event hoster input how many people showed up (for engagement metrics?)
    --> add user ratings and feedback to the specific social in the first place
--> access malpractice reports (via reportID or eventID)
    --> add malpractice reports to database in the first place
'''

def addRating(cursor, eventID, rating):
    """
    Adds user rating to the corresponding table.

    (*) User rating is a positive integer between 1 and 5.
    """
    cursor.execute("SELECT averageRating, ratingCount FROM Raing WHERE eventID = (?)", (eventID,))
    ratingStats = cursor.fetchall()
    newCount = ratingStats[1] + 1
    newAvg = round((ratingStats[0]*ratingStats[1] + rating) / newCount)
    cursor.execute("UPDATE Event SET averageRating = (?), ratingCount = (?) WHERE eventID = (?)", (newAvg, newCount, eventID))

def getRating(cursor, eventID):
    """
    Retrieves average user rating for a given eventID.
    """
    cursor.execute("SELECT averageRating FROM Event WHERE eventID = (?)", (eventID,))

### [FEEDBACK TABLE] ###
# A 'Feedback' Table where we store (feedbackID, eventID, feedbackData?)

def addFeedback(cursor, eventID, feedbackData):
    """
    Adds user feedback to the corresponding table.
    """
    # format feedback data?
    # feedbackData = format(feedbackData)
    cursor.execute("INSERT INTO Feedback VALUES (?,?)", (eventID, feedbackData))

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

def addReport(cursor, eventID, reportData):
    """
    Adds a malpractice report to the corresponding table.
    """
    # format report data?
    # reportData = format(reportData)
    cursor.execute("INSERT INTO Report VALUES (?,?)", (eventID, reportData))

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
