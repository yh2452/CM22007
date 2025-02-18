# import sqlite3, pandas shouldn't be needed

'''
USER DATABASE
--> access socials a user has attended in the past
    --> mark events as 'attended' once the event date has passed
--> access socials a user is planning to attend
    --> mark events accordingly when users first select to 'attend' (similar for 'unattend')
--> access events users have previously pinned
    --> mark events as 'pinned' for users (are we storing eventID or something inside the user database?)
--> access followed societies
    --> mark societies as 'followed' when users first select to 'follow' (similar for 'unfollow')

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
