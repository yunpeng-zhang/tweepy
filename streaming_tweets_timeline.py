# streaming_tweets_timeline.py
# 1. verify api info
# 2. stream home tweets
# 3. stream user tweets
# 4. stream on key words
# 5. streaming using strem StreamListener

# Twitter API authentication

import tweepy


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

# Streaming tweets from home timeline
public_tweet = api.home_timeline(count=5)

for tweet in public_tweet:
    print("-->",tweet.text)

# Streaming tweets from user timeline
user = "CryptoAlgoWheel"
public_tweet = api.user_timeline(id=user,count=5)

for tweet in public_tweet:
    print("-->",tweet.text)

# Retrieve tweets
result = api.search(['Bitcoin','Cryptocurrency','Blockchain'], lang='en', count=10)
import pprint
# JSON keys
pprint.pprint(result[0]._json.keys())

pprint.pprint(result[4].entities['hashtags'])