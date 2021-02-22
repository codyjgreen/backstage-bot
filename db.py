import sqlite3
from datetime import datetime
today = datetime.today().strftime('%Y-%m-%d')

# Global since they are used everywhere
# FIXME: better way?
conn = None
c = None

'''
Open connection and create DB if not exxist
'''
def db_init(dbfile_name='backstage_meet_log.db'):
    global conn, c
    conn = sqlite3.connect(dbfile_name)
    c = conn.cursor()

    # Create table
    c.execute('''
    create table IF NOT EXISTS matching(
    star1 VARCHAR(100) NOT NULL,
    star2 VARCHAR(40) NOT NULL,
    recent_meet_date DATE,
    meet_count INT,
    PRIMARY KEY ( star1, star2 )
    );
    ''')
    
    # Save (commit) the changes
    conn.commit()

'''
Add star1, star2 pairs into DB if not exist
and remove inactive users
'''
def db_add_stars (stars):
    for star1 in stars:
        for star2 in stars:
            if star1 < star2: # Order matters. A, B vs B, A ==> Always make sure it's A, B
                # check if exist
                # FIXME: better way using a simple SQL?
                exist = c.execute("SELECT 1 FROM matching where star1='{}' and star2='{}'".format(star1, star2))
                
                # Let's add them
                if exist.fetchone() == None:
                    print("Let's insert", star1, star2, "pair!") 
                    c.execute("INSERT INTO matching VALUES ('{}', '{}', '{}', 0)"
                    .format(star1, star2, today)) 
    
    # See if we need to remove anyone
    remove_inactive_users_in_db (stars)

    # Save (commit) the changes
    conn.commit()

'''
remove inactive users from DBMS
'''
def remove_inactive_users_in_db (stars):
    exec = c.execute("SELECT star1, star2 from matching")
    users_in_db = set()

    # Add all star1, star2 into a set
    # FIXME: a better way to using SQL?
    for row in exec:
        star1 = row[0]
        star2 = row[1]
        users_in_db.add(star1)
        users_in_db.add(star2)
    
    # if not active, remove
    # TODO: test more, but hard to test
    for user in users_in_db:
        if user not in stars:
            print(user, "not in stars anymore!")
            c.execute("DELETE from matching where star1='{}' or star2='{}'".format(user, user))
        else: 
            print(user, "is in stars. Cool!")

    # Save (commit) the changes
    conn.commit()

'''
Get matches order by meet_count and recent meet date
'''
def db_get_matches():
    matched = set()
    matched_pairs = []
    for row in c.execute('SELECT star1, star2, meet_count, recent_meet_date FROM matching ORDER BY meet_count, recent_meet_date'):
        star1 = row[0]
        star2 = row[1]
        # FIXME: can we do using a SQL?
        if star1 not in matched and star2 not in matched:
            # Upsate sql
            matched.add(star1)
            matched.add(star2)
            matched_pairs.append((star1, star2))

    # Upsate DB after the select
    # We assume they will meet
    for star1, star2 in matched_pairs:
        c.execute("UPDATE matching SET meet_count = meet_count + 1, recent_meet_date ='{}' WHERE star1 = '{}' and star2 = '{}' " 
            .format(today, star1, star2))

    # Save (commit) the changes
    conn.commit()

    return matched_pairs

def db_close():
    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()

if __name__ == '__main__':
    db_init()
    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()
