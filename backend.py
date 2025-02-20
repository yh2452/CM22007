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
# An 'Attended' Table where we store (userid, eventid)

def toggleAttend(cursor, userid, eventid):
    """
    Allows a user to mark or unmark an event for future attending.
    """
    cursor.execute("SELECT eventid FROM Attended WHERE userid = (?) AND eventid = (?)", (userid, eventid))
    event = cursor.fetchall()
    if not event:
        cursor.execute("INSERT INTO Attended VALUES (?,?)",(userid, eventid))
    else:
        cursor.execute("DELETE FROM Attended WHERE userid = (?) AND eventid = (?)", (userid, eventid))

def getAttendedEvents(cursor, userid, flag):
    """
    Return all socials the user has attended in the past, or ones they are planning to attend.

    flag: TRUE = past attended events, FALSE = future events they plan to attend
    """
    date = datetime.datetime.now()
    
    if flag:
        cursor.execute("SELECT Event.* FROM Event INNER JOIN Attended ON Event.eventid=Attended.eventid WHERE Attended.userid = (?) AND Event.date < (?)", (userid, date))
    else:
        cursor.execute("SELECT Event.* FROM Event INNER JOIN Attended ON Event.eventid=Attended.eventid WHERE Attended.userid = (?) AND Event.date >= (?)", (userid, date))

    return cursor.fetchall()  # unless we want to format each result somehow

### [PINNED TABLE] ###
# A 'Pinned' Table where we store (userid, eventid)

def togglePin(cursor, userid, eventid):
    """
    Allows a user to pin or unpin an event.
    """
    cursor.execute("SELECT eventid FROM Pinned WHERE userid = (?) AND eventid = (?)", (userid, eventid))
    event = cursor.fetchall()
    if not event:
        cursor.execute("INSERT INTO Pinned VALUES (?,?)", (userid, eventid))
    else:
        cursor.execute("DELETE FROM Pinned WHERE userid = (?) AND eventid = (?)", (userid, eventid))

def getPinnedEvents(cursor, userid):
    """
    Returns all events the user has pinned.
    """
    cursor.execute("SELECT Event.* FROM Event INNER JOIN Pinned ON Event.eventid=Pinned.eventid WHERE Attended.userid = (?)", (userid,)) 
    return cursor.fetchall()  # unless we want to format each result somehow

### [FOLLOWED TABLE] ###
# A 'Followed' Table where we store (userid, societyid)

def toggleFollow(cursor, userid, socid):
    """
    Allows a user to follow or unfollow a society.
    """
    cursor.execute("SELECT societyid FROM Followed WHERE userid = (?) AND societyid (?)", (userid, socid))
    soc = cursor.fetchall()
    if not soc:
        cursor.execute("INSERT INTO Followed VALUES (?,?)", (userid, socid))
    else:
        cursor.execute("DELETE FROM Followed WHERE userid = (?) AND societyid (?)", (userid, socid))

def getFollowed(cursor, userid):
    """
    Returns all societies the user follows.
    """
    cursor.execute("SELECT Society.* FROM Society INNER JOIN Followed ON Society.societyid=FOLLOWED.societyid WHERE Followed.userid = "+userid)
    return cursor.fetchall()  # unless we want to format each result somehow

'''
SOCIAL DATABASE
(*) Seems like we are pulling the society info directly from the SU website? How do we do that
--> access social/event info (listed in acceptance test 2.1)
    --> creation of socials by users/committee members
--> access engagement metrics (no. of people interested, how many turned up for previous socials, etc.?)

FEEDBACK DATABASE
--> access user ratings/feedback for a specific social
    --> generate an entry for each social once the event date has passed 
        --> maybe let event hoster input how many people showed up (for engagement metrics?)
    --> add user ratings and feedback to the specific social in the first place
--> malpractice reports
    --> add malpractice reports to database in the first place
'''
