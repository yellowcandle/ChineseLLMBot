import os
import re
import feedparser
import tweepy
from litellm import completion

# Move dotenv import here if needed
# from dotenv import load_dotenv
# load_dotenv()


def tweet_content(summary_text):
  # Authenticate to Twitter
  client = tweepy.Client(
      consumer_key=os.environ['TWITTER_API_KEY'],
      consumer_secret=os.environ['TWITTER_API_SECRET'],
      access_token=os.environ['TWITTER_ACCESS_TOKEN'],
      access_token_secret=os.environ['TWITTER_ACCESS_SECRET']
  )
  # Post a tweet
  try:
      client.create_tweet(text=summary_text)
      print("Tweet successfully posted!")
  except tweepy.TweepyException as e:
      print(f"An error occurred: {e}")


def response_output(response):
  # Retrieve the actual message content from the response
  content = response['choices'][0]['message']['content']
  return content  # Return the content so it can be used elsewhere


url = 'https://www.info.gov.hk/gia/rss/general_zh.xml'
feed = feedparser.parse(url)
first_summary_text = None

if feed.entries:
  first_summary_text = re.sub('<[^<]+?>', '',
                              feed.entries[0].title)  # Remove HTML tags

my_secret = os.environ['OPENAI_API_KEY']
if first_summary_text:
  response = completion(model="gpt-3.5-turbo",
                        messages=[{
                            "content": "使用台灣作家瓊瑤的寫作風格重寫輸入的字句，必須在140字元以內!",
                            "role": "system"
                        }, {
                            "content": first_summary_text,
                            "role": "user"
                        }])

# Now, we get the content from the response output using response_output function
response_text = response_output(response)  # This captures the return value from response_output
# Finally, tweet the content if it exists

if response_text:
  tweet_text = first_summary_text + "\n\n" + response_text
  tweet_content(tweet_text)
  print(tweet_text)