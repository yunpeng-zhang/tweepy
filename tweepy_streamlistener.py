import tweepy
from tweepy.streaming import StreamListener
import time
import psycopg2
class MyStreamListener(tweepy.streaming.StreamListener):

    def __init__(self, time_limit=300):
        self.start_time = time.time()
        self.limit = time_limit
        super(MyStreamListener, self).__init__()

    def on_connect(self):
        print("Connected to Twitter API.")

    def on_status(self, status):

        # Tweet ID
        tweet_id = status.id

        # User ID
        user_id = status.user.id
        # Username
        username = status.user.name

        # Tweet
        if status.truncated == True:
            tweet = status.extended_tweet['full_text']
            hashtags = status.extended_tweet['entities']['hashtags']
        else:
            tweet = status.text
            hashtags = status.entities['hashtags']

        # Read hastags
        hashtags = read_hashtags(hashtags)

        # Retweet count
        retweet_count = status.retweet_count
        # Language
        lang = status.lang

        # If tweet is not a retweet and tweet is in English
        if not hasattr(status, "retweeted_status") and lang == "en":
            # Connect to database
            dbConnect(user_id, username, tweet_id,
                      tweet, retweet_count, hashtags)

        if (time.time() - self.start_time) > self.limit:

            print('end time:', time.time(), 'start time', self.start_time, 'passed time', self.limit)            
            return False

    def on_error(self, status_code):
        if status_code == 420:
            # Returning False in on_data disconnects the stream
            return False

# Extract hashtags
def read_hashtags(tag_list):
    hashtags = []
    for tag in tag_list:
        hashtags.append(tag['text'])
    return hashtags

# Insert Tweet data into database
def dbConnect(user_id, user_name, tweet_id, tweet, retweet_count, hashtags):
    
    conn = psycopg2.connect(host="localhost",database="TwitterDB",port=5432,user='postgres',password='790213Aa')
    
    cur = conn.cursor()

    # insert user information
    command = '''INSERT INTO TwitterUser (user_id, user_name) VALUES (%s,%s) ON CONFLICT
                 (User_Id) DO NOTHING;'''
    cur.execute(command,(user_id,user_name))
    print('user infomariton is inserted successfully.')

    # insert tweet information
    command = '''INSERT INTO TwitterTweet (tweet_id, user_id, tweet, retweet_count) VALUES (%s,%s,%s,%s);'''
    cur.execute(command,(tweet_id, user_id, tweet, retweet_count))
    print('tweet information is inserted successfully.')

    # insert entity information
    for i in range(len(hashtags)):
        hashtag = hashtags[i]
        command = '''INSERT INTO TwitterEntity (tweet_id, hashtag) VALUES (%s,%s);'''
        cur.execute(command,(tweet_id, hashtag))
        print(f'TwitterEntity {i} is inserted successfully.')
    
    # Commit changes
    conn.commit()
    
    # Disconnect
    cur.close()
    conn.close()

api_key =  'x9gnpL855ZWKD3FMAMmAQyiLs' # api_key
api_secret_key = 'H4UkqL4VwA12xoKHNOEwKXEaTOHTTTZ2qlrDX8gfXa7MCmRzse' # api_secret_key
access_token =  '747814153-AmhAIPIklSdnJ1YV3LQ5KRJkgDKnf1ksUODu5WFv'  # access_token
access_token_secret = 'BcPvBCFJewPiMKHEbbtEOJHc4EQtbyFjgsrVLuiQzxTLv' # access_token_secret

# authorize the API Key
authentication = tweepy.OAuthHandler(api_key, api_secret_key)

# authorization to user's access token and access token secret
authentication.set_access_token(access_token, access_token_secret)

# call the api
api = tweepy.API(authentication)
# Streaming tweets

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener,
                        tweet_mode="extended")
myStream.filter(track=['bitcoin','crypto']) # will disconnect after 300 seconds.
# runtime = 60 #Tracking for 60 seconds
# time.sleep(runtime)
# myStream.disconnect() # discounnect after 60 seconds