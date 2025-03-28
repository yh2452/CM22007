import sqlite3
import datetime
import hashlib
import os
import bcrypt
from better_profanity import profanity
import datetime
import pytest 

profanity.load_censor_words()

def hash(data):
    '''
    Hashes a given input (password) with salt 
    '''
    salt = bcrypt.gensalt() # generates salt
    hash_object = bcrypt.hashpw(data.encode(), salt) # creates hashed data
    return hash_object

def checkHash(data, hashed_data):
    """
    Checks the input data against the hashed data stored in the database
    """
    return bcrypt.checkpw(data.encode(), hashed_data)


def sanitiseInput(data):
    """
    Checks if there is any profanity in any given data
    """
    if profanity.contains_profanity(data):
        return None
    return data
    

def get_db_conn_cursor():
    # NOTE: set the database link to wherever we're keeping the main database. 
    # for me (ollie), the commented line below that was originally there does not work.
    connection = sqlite3.connect('MySocials/table.db')
    #connection = sqlite3.connect('table.db')
    cursor = connection.cursor()
    return connection, cursor

'''
USERS
--> access socials a user has Attending in the past
    --> mark events as 'Attending' once the event date has passed
    --> Calendar for future events user is planning to attend
--> access socials a user is planning to attend
    --> mark events accordingly when users first select to 'attend' (similar for 'unattend')
--> access events users have previously pinned
    --> mark events as 'pinned' for users
--> access followed societies
    --> mark societies as 'followed' when users first select to 'follow' (similar for 'unfollow')
'''

### [USER TABLE] ###
# A 'User' Table where we store (userID, forename, surname, username, password, email)
# Note that the password field is the hash of the password
# TODO: determine how account deletion functions (username or email required?)
# TODO: check database has autoincrement for userID field
# TODO: finish writing addUser and removeUser functions

def isUserDuplicate(cursor, username, email):
    """
    Called when registering a user. Returns true if given username and email are not in use by other users. 
    """
    cursor.execute("SELECT userID FROM User WHERE username = (?) OR email = (?)", (username, email))
    status = cursor.fetchall()
    if status:
        #i.e. duplicate users present
        return True
    else: 
        return False

def addUser(cursor, forename, surname, username, password, email):
    # remember to hash the password - all you have to do is call the hash subroutine = hash(password)
    password = hash(password)
    cursor.execute("INSERT INTO User (username, password, forename, surname, email) VALUES (?,?,?,?,?)", (username, password, forename, surname, email))
    print(f"User {username} successfully registered.")

def removeUser(cursor):
    pass

def getUserFromUsername(cursor, username):
    """
    Checks to see if a given User exists from username
    """
    cursor.execute("SELECT * FROM User WHERE username = (?)", (username,))
    user = cursor.fetchone()
    return user



### [ATTENDING TABLE] ###
# An 'Attending' Table where we store (userID, eventID, notificationFlag)

def toggleAttend(cursor, userID, eventID):
    """
    Allows a user to mark or unmark an event for future attending.
    """
    cursor.execute("SELECT eventID FROM Attending WHERE userID = (?) AND eventID = (?)", (eventID, userID))
    event = cursor.fetchall()
    if not event:
        cursor.execute("INSERT INTO Attending VALUES (?,?,?)", (eventID, userID, 0))
    else:
        cursor.execute("DELETE FROM Attending WHERE userID = (?) AND eventID = (?)", (eventID, userID))
    
def toggleAttendNotifs(cursor, userID, eventID):
    """
    Toggles email notifications for a specific event.
    """
    cursor.execute("SELECT notificationFlag FROM Attending WHERE userID = (?) AND eventID = (?)", (userID, eventID))
    status = cursor.fetchone()[0]
    if status == 1:
        cursor.execute("UPDATE Attending SET notificationFlag = 0 WHERE userID = (?) AND eventID = (?)", (userID, eventID))
    else:
        cursor.execute("UPDATE Attending SET notificationFlag = 1 WHERE userID = (?) AND eventID = (?)", (userID, eventID))

def getAttendNotifEmails(cursor, eventID):
    """
    Returns email addresses of all users who have notifications on for a specific event.
    """
    cursor.execute("SELECT User.email FROM User INNER JOIN Attending ON User.userID=Attending.userID WHERE Attending.eventID = (?) AND Attending.notificationFlag = 1", (eventID,))
    return cursor.fetchall() 
    

def getAttendingEvents(cursor, userID, flag):
    """
    Return all socials the user has Attending in the past, or ones they are planning to attend.

    flag: TRUE = past Attending events, FALSE = future events they plan to attend
    """
    date = datetime.datetime.now()
    
    if flag:
        cursor.execute("SELECT Event.* FROM Event INNER JOIN Attending ON Event.eventID=Attending.eventID WHERE Attending.userID = (?) AND Event.eventDate < (?)", (userID, date))
    else:
        cursor.execute("SELECT Event.* FROM Event INNER JOIN Attending ON Event.eventID=Attending.eventID WHERE Attending.userID = (?) AND Event.eventDate >= (?)", (userID, date))

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
    cursor.execute("SELECT Event.* FROM Event INNER JOIN Pinned ON Event.eventID=Pinned.eventID WHERE Attending.userID = (?)", (userID,)) 
    return cursor.fetchall()  # any result formatting?

### [FOLLOWED TABLE] ###
# A 'Followed' Table where we store (userID, societyID, notificationFlag)

def toggleFollow(cursor, userID, societyID):
    """
    Allows a user to follow or unfollow a society.
    """
    cursor.execute("SELECT societyID FROM Followed WHERE userID == (?) AND societyID == (?)", (userID, societyID))
    soc = cursor.fetchall()
    if not soc:
        cursor.execute("INSERT INTO Followed VALUES (?,?,?)", (userID, societyID, 0))
    else:
        cursor.execute("DELETE FROM Followed WHERE userID == (?) AND societyID == (?)", (userID, societyID))

def getFollowed(cursor, userID):
    """
    Returns all societies the user follows.
    """
    cursor.execute("SELECT Society.* FROM Society INNER JOIN Followed ON Society.societyID=Followed.societyID WHERE Followed.userID = (?)", (userID,))
    return cursor.fetchall()  # any result formatting?

def toggleFollowNotifs(cursor, userID, societyID):
    """
    Toggles email notifications for a specific society.
    """
    cursor.execute("SELECT notificationFlag FROM Followed WHERE userID = (?) AND societyID = (?)", (userID, societyID))
    status = cursor.fetchone()[0]
    if status == 1:
        cursor.execute("UPDATE Followed SET notificationFlag = 0 WHERE userID = (?) AND societyID = (?)", (userID, societyID))
    else:
        cursor.execute("UPDATE Followed SET notificationFlag = 1 WHERE userID = (?) AND societyID = (?)", (userID, societyID))

def getSocietyNotifEmails(cursor, societyID):
    """
    Returns email addresses of all users who have notifications on for a specific society.
    """
    cursor.execute("SELECT User.email FROM User INNER JOIN Followed ON User.userID=Followed.userID WHERE Followed.societyID = (?) AND Followed.notificationFlag = 1", (societyID,))
    return cursor.fetchall() 

### [COMMITTEE TABLE] ###
# A 'Committee' Table where we store (userID, societyID, adminFlag)
# 'admin' is a boolean determining the administrator status of the user within the society.

def addMember(cursor, userID, societyID):
    """
    Adds a user as a society committee member.
    """
    cursor.execute("SELECT adminFlag FROM Committee WHERE userID = (?) AND societyID = (?)", (userID, societyID))
    status = cursor.fetchall()
    if not status:
        cursor.execute("INSERT INTO Committee VALUES (?,?,?)", (userID, societyID, 0))

def removeMember(cursor, userID, societyID):
    """
    Removes a user from society committee member status.
    """
    cursor.execute("SELECT adminFlag FROM Committee WHERE userID = (?) AND societyID = (?)", (userID, societyID))
    status = cursor.fetchall()
    if status:
        cursor.execute("DELETE FROM Committee WHERE userID = (?) AND societyID = (?)", (userID, societyID))

def toggleAdmin(cursor, userID, societyID):
    """
    Sets / unsets a user as a society administrator.
    """
    cursor.execute("SELECT adminFlag FROM Committee WHERE userID = (?) AND societyID = (?)", (userID, societyID))
    status = cursor.fetchall()[0][0]
    if status:
        cursor.execute("UPDATE Committee SET adminFlag = 0 WHERE userID = (?) AND societyID = (?)", (userID, societyID))
    else:
        cursor.execute("UPDATE Committee SET adminFlag = 1 WHERE userID = (?) AND societyID = (?)", (userID, societyID))

def getAdminSocs(cursor, userID):
    """
    Retrieves all societies for which a user is administrator for.
    """
    cursor.execute("SELECT societyID FROM Committee WHERE userID = (?) AND adminFlag = 1", (userID,))
    return cursor.fetchall()


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

def getsocietyID(cursor, name):
    """
    Obtains the societyID for backend use
    """
    cursor.execute ("SELECT societyID FROM Society WHERE societyName = ?", (name,))
    return cursor.fetchall()


def addSocial(cursor, societyID, userID, eventName, eventDate, eventDescription, eventTags):
    """
    Allows a committee member to create a social
    """
    # will be linked to notifications
    cursor.execute("INSERT INTO Event (societyID, userID, eventName, eventDate, eventDescription, ratingCount, averageRating, eventTags) VALUES (?,?,?,?,?,?,?,?)", (societyID, userID, eventName, eventDate, eventDescription, 0.0 , 0, eventTags,))

def editSocial(cursor, eventID, name, date, description, data):
    """
    Allows a user to edit a social.
    """
    # will be linked to notifications
    cursor.execute("UPDATE Event SET eventName = (?), eventDate = (?), eventDescription = (?), eventData = (?) WHERE eventID = (?)", (name, date, description, data, eventID))

def deleteSocial(cursor, eventID):
    """
    Allows users to delete a social.
    """
    # will be linked to notifications
    cursor.execute("DELETE FROM Event WHERE eventID = (?)", (eventID))

def getAccessibleSocials(cursor, userID):
    """
    Presents all available events that the user can edit or delete, taking into account Committee Admin permissions
    """
    cursor.execute("SELECT eventID FROM Event WHERE userID = (?)", (userID,))
    ownEvents = cursor.fetchall()

    adminSocs = getAdminSocs(cursor, userID)
    societyEvents = []
    for societyID in adminSocs:
        cursor.execute("SELECT eventID FROM Event WHERE societyID = (?)", (societyID,))
        societyEvents += cursor.fetchall()
    
    return ownEvents + societyEvents
    

def getSocialData(cursor, societyID, eventID, metric=None):
    """
    Allows data about a social to be found
    """
    #### do we want to show eventDescription (tags) as well? - Jamie
    # what if they type in more than one metric?????????
    # unless we just return all metrics??????? therefore we don't need to take in metric as a parameter
    cursor.execute("SELECT eventData FROM Event WHERE societyID = (?) AND eventID = (?)", (societyID, eventID))
    return cursor.fetchall()

def filterSocials (cursor, filters):
    """
    Filters the socials that the user sees
    """
    # I guess filters will be an array? 
    if filters:
        query = "SELECT eventName FROM Event WHERE "
        keywords = []
        for loop in range (len(filters)):
            if loop == 0:
                query += "eventTags LIKE (?)"
            else:
                query += " OR eventTags LIKE (?)"
            keywords.extend([f"%{filters[loop]}%"])
        cursor.execute(query, keywords)
    else:
        cursor.execute("SELECT eventName FROM Event")
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
    cursor.execute("SELECT averageRating, ratingCount FROM Event WHERE eventID = (?)", (eventID,))
    ratingStats = cursor.fetchall()
    newCount = ratingStats[0][1] + 1
    newAvg = round((ratingStats[0][0]*ratingStats[0][1] + rating) / newCount)
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
    cursor.execute("INSERT INTO Feedback (eventID, feedbackData) VALUES (?,?)", (eventID, feedbackData))

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
    cursor.execute("INSERT INTO Report (eventID, reportData) VALUES (?,?)", (eventID, reportData,))

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


# SOFTWARE TESTING

# def insert_passwords(connection, cursor):
#     users_data = [4,5,6,7,8,9]
#     passwords = ['securepass1', 'securePass1', 'securepass123', 'securePass234', 'Password123', 'Pass_word']
#     for loop in range (len(users_data)):
#         cursor.execute("""
#             UPDATE User
#             SET password = ?
#             WHERE UserID = ?
#         """, (hash(passwords[loop]), users_data[loop])) 
#     print("Done")
#     connection.commit()
#     connection.close()

def test_HashPasswords():
    password = "securepass123"
    hashed = hash(password)
    assert checkHash(password, hashed) == True
    assert checkHash("securePass123", hashed) == False

def test_Filtering():
    try:
        connection, cursor = get_db_conn_cursor()
        filter = "Off Campus"
        data = filterSocials(cursor, [filter])
        assert data[0][0] == "Pub Social"
    finally:
        connection.close()

def test_Profanity():
    goodText = "Anime Marathon Social"
    badText = "The Damn You Social"
    assert sanitiseInput(goodText) == goodText
    assert sanitiseInput(badText) == None


def test_ToggleAttendEvent():
    try:
        connection, cursor = get_db_conn_cursor()
        userID = 101
        eventID = 101
        toggleAttend(cursor, userID, eventID)
        cursor.execute("SELECT * FROM Attending WHERE userID==(?) AND eventID==(?)", (userID, eventID))
        assert cursor.fetchone() is not None

        toggleAttend(cursor, userID, eventID)
        cursor.execute("SELECT * FROM Attending WHERE userID==(?) AND eventID==(?)", (userID, eventID))
        assert cursor.fetchone() is None
    finally:
        connection.close()

def test_ToggleAttendNotifs():
    try:
        connection, cursor = get_db_conn_cursor()
        cursor.execute("SELECT * FROM Attending")
        eventID, userID, flag = cursor.fetchone()
    
        toggleAttendNotifs(cursor, userID, eventID)
        connection.commit()
        cursor.execute("SELECT notificationFlag FROM Attending WHERE userID==(?) AND eventID==(?)", (userID, eventID))
        assert cursor.fetchone()[0] is not flag
     
        toggleAttendNotifs(cursor, userID, eventID)
        connection.commit()
        cursor.execute("SELECT notificationFlag FROM Attending WHERE userID==(?) AND eventID==(?)", (userID, eventID))
        assert cursor.fetchone()[0] is flag
    finally:
        connection.close()

def test_ToggleFollowSociety():
    try:
        connection, cursor = get_db_conn_cursor()
        userID = 9
        societyID = 101
        
        toggleFollow(cursor, userID, societyID)
        connection.commit()
        cursor.execute("SELECT * FROM Followed WHERE userID==(?) AND societyID==(?)", (userID, societyID))
        assert cursor.fetchone() is not None

        toggleFollow(cursor, userID, societyID)
        connection.commit()
        cursor.execute("SELECT * FROM Followed WHERE userID==(?) AND societyID==(?)", (userID, societyID))
        assert cursor.fetchone() is None
    finally:
        connection.close()

def test_ToggleFollowNotifs():
    try:
        connection, cursor = get_db_conn_cursor()
        cursor.execute("SELECT * FROM Followed")
        userID, societyID, flag = cursor.fetchone()
    
        toggleFollowNotifs(cursor, userID, societyID)
        connection.commit()
        cursor.execute("SELECT notificationFlag FROM Followed WHERE userID==(?) AND societyID==(?)", (userID, societyID))
        assert cursor.fetchone()[0] is not flag
     
        toggleFollowNotifs(cursor, userID, societyID)
        connection.commit()
        cursor.execute("SELECT notificationFlag FROM Followed WHERE userID==(?) AND societyID==(?)", (userID, societyID))
        assert cursor.fetchone()[0] is flag
    finally:
        connection.close()

def test_GiveFeedback():
    try:
        connection, cursor = get_db_conn_cursor()
        eventID = 101
        feedback = "This was a great event that I thoroughly enjoyed. Very welcome to newcomers."
        addFeedback(cursor, eventID, feedback)
        connection.commit()
        cursor.execute("SELECT feedbackData FROM Feedback WHERE eventID == (?)", (eventID,))
        result = cursor.fetchall()[0][0]
        assert result == feedback
        cursor.execute("DELETE FROM Feedback WHERE eventID == (?)", (eventID,))
    finally:
        connection.close()

def test_FileReport():
    try:
        connection, cursor = get_db_conn_cursor()
        eventID = 101
        report = "Social Host was extremely rude"
        addReport(cursor, eventID, report)
        connection.commit()
        cursor.execute("SELECT reportData FROM Report WHERE eventID == (?)", (eventID,))
        result = cursor.fetchall()[0][0]
        assert result == report
        cursor.execute("DELETE FROM Report WHERE eventID == (?)", (eventID,))
    finally:
        connection.close()

def test_Rating():
    try:
        connection, cursor = get_db_conn_cursor()
        eventID = 4
        rating = 3
        cursor.execute("SELECT averageRating, ratingCount FROM Event WHERE eventID = (?)", (eventID,))
        ratingStats = cursor.fetchall()
        print(ratingStats)
        expectedCount = ratingStats[0][1] + 1
        expectedAvg = round((ratingStats[0][0]*ratingStats[0][1] + rating) / expectedCount)
        addRating(cursor, eventID, rating)
        connection.commit()
        cursor.execute("SELECT averageRating, ratingCount FROM Event WHERE eventID = (?)", (eventID,))

        ratingStats = cursor.fetchall()
        currentCount = ratingStats[0][1]
        currentAvg = ratingStats[0][0]
        assert expectedAvg == currentAvg
        assert currentCount == expectedCount
    finally:
        connection.close()

def test_SeeAttendees():
    try:
        connection, cursor = get_db_conn_cursor()
        eventID = 101
        attendees = 10
        for loop in range (1, attendees + 1):
            cursor.execute("INSERT INTO Attending (eventID, userID) VALUES (?, ?)", (eventID, loop,))
        connection.commit()
        registered_attendees = []
        for loop in range (1, attendees + 1):
            cursor.execute("SELECT userID FROM Attending WHERE eventID == (?)", (eventID,))
            registered_attendees.append(cursor.fetchone)

        cursor.execute("DELETE FROM Attending WHERE eventID = ?", (eventID,))
        assert attendees == len(registered_attendees)
        connection.commit()
    finally:
        connection.close()
        
def test_CreateSocial():
    try:
        connection, cursor = get_db_conn_cursor()
        userID = 101
        societyID = 101
        eventName = "Pub Lecture"
        eventDate = "2025-03-25 19:00"
        eventDescription = "Come watch your favourite lecturers give a lecture in the pub!"
        eventTags = "Off Campus, Fun, Socialising"
        addSocial(cursor, societyID, userID, eventName, eventDate, eventDescription, eventTags)
        connection.commit()
    
        cursor.execute("SELECT * FROM Event WHERE societyID == (?) AND userID == (?) AND eventName == (?) AND "
        "eventDate == (?) AND eventDescription == (?) AND eventTags == (?)", (societyID, userID, eventName, eventDate, eventDescription, eventTags,))
        result = cursor.fetchone()
        assert result is not None
        cursor.execute("DELETE FROM Event WHERE eventID = ?", (result[0],))

        connection.commit()
    finally:
        connection.close()

def test_TogglePin():
    try:
        connection, cursor = get_db_conn_cursor()
        userID = 9
        eventID = 101
        togglePin(cursor, userID, eventID)
        cursor.execute("SELECT * FROM Pinned WHERE userID==(?) AND eventID==(?)", (userID, eventID))
        assert cursor.fetchone() is not None

        togglePin(cursor, userID, eventID)
        cursor.execute("SELECT * FROM Pinned WHERE userID==(?) AND eventID==(?)", (userID, eventID))
        assert cursor.fetchone() is None
    finally:
        connection.close()

def test_TestCommittee():
    try:
        connection, cursor = get_db_conn_cursor()
        userID = 101
        societyID = 101
        addMember(cursor, userID, societyID)
        connection.commit()
        cursor.execute("SELECT * FROM Committee WHERE societyID == (?) AND userID == (?)",(societyID,userID))
        result = cursor.fetchone()
        assert result is not None
        removeMember(cursor, userID, societyID)
        connection.commit()
        cursor.execute("SELECT * FROM Committee WHERE societyID == (?) AND userID == (?)",(societyID,userID))
        result = cursor.fetchone()
        assert result is None
    finally:
        connection.close()

def test_ToggleAdmin():
    try:
        connection, cursor = get_db_conn_cursor()
        userID = 101
        societyID = 101

        addMember(cursor, userID, societyID)
        connection.commit()

        toggleAdmin(cursor, userID, societyID)
        cursor.execute("SELECT * FROM Committee WHERE userID==(?) AND societyID==(?)", (userID, societyID))
        assert cursor.fetchone()[2] is 1

        toggleAdmin(cursor, userID, societyID)
        cursor.execute("SELECT * FROM Committee WHERE userID==(?) AND societyID==(?)", (userID, societyID))
        assert cursor.fetchone()[2] is 0

        removeMember(cursor, userID, societyID)
        connection.commit()
    finally:
        connection.close()
#insert_passwords(connection, cursor) # inserts some fake passwords to the data

# issues found
# toggle attend added the event ID and user ID the wrong way around
# when adding items to a table and assuming the table will autoincrement, the items actually need to be in a tuple
# rating table doesn't actually exist
# when reading in the rating values the indexes were actually wrong
# 