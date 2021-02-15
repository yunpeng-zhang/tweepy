# Table creation
commands = (# Table 1
            '''Create Table TwitterUser(User_Id BIGINT PRIMARY KEY, User_Name TEXT);''',
            # Table 2
            '''Create Table TwitterTweet(Tweet_Id BIGINT PRIMARY KEY,
                                         User_Id BIGINT,
                                         Tweet TEXT,
                                         Retweet_Count INT,
                                         CONSTRAINT fk_user
                                             FOREIGN KEY(User_Id)
                                                 REFERENCES TwitterUser(User_Id));''',
            # Table 3
            '''Create Table TwitterEntity(Id SERIAL PRIMARY KEY,
                                         Tweet_Id BIGINT,
                                         Hashtag TEXT,
                                         CONSTRAINT fk_user
                                             FOREIGN KEY(Tweet_Id)
                                                 REFERENCES TwitterTweet(Tweet_Id));''')

import psycopg2

# Connection to database server
conn = psycopg2.connect(host="localhost",database="TwitterDB",port=5432,user='postgres',password='790213Aa')
# Create cursor to execute SQL commands
cur = conn.cursor()

# Execute SQL commands
i=0
for command in commands:
    # Create tables
    cur.execute(command)
    # print(f'Table {i} is created successfully.')

# Close communication with server
conn.commit()
cur.close()
conn.close()
