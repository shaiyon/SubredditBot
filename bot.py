# bot.py
# reddit bot that replies to comments invoking it
# Shaiyon Hariri

import os
import sys
import praw
import config
import re
from time import sleep
from random import randrange
from generate import generate
import json
import requests


def login():
    reddit = praw.Reddit(client_id=config.client_id,
                         client_secret=config.client_secret,
                         user_agent=f'{config.bot_name} v0.1 by Shaiyon Hariri',
                         username=config.username,
                         password=config.password)
    print("Logged in.")
    return reddit

# Parse json file
def json_dump_and_parse(file_name, request):
    with open(file_name, "w+") as f:
        json.dump(request.json(), f, sort_keys=True,
                  ensure_ascii=False, indent=4)
    with open(file_name) as f:
        data = json.load(f)
    return data

# Reply to user's comment and handle errors appropriately
def reply_to_comment(reddit, comment_id, comment_reply, comment_subreddit, comment_author, comment_body):
    try:
        # Use reddit API to reply to comment using comment id
        comment_to_be_replied_to = reddit.comment(id=comment_id)
        comment_to_be_replied_to.reply(comment_reply)
        print (f"\nReply details:\nSubreddit: r/{comment_subreddit}\nComment:\"{comment_body}\"\nReply:\"{comment_reply}\"\nUser: u/{comment_author}\a")

    except Exception as e:
        time_remaining = 15
        if (str(e).split()[0] == "RATELIMIT:"):
            for i in str(e).split():
                if (i.isdigit()):
                    time_remaining = int(i)
                    break
            if (not "seconds" or not "second" in str(e).split()):
                time_remaining += 10

        print(str(e.__class__.__name__) + ": " + str(e))
        for i in range(time_remaining, 0, -5):
            print("Retrying in", i, "seconds..")
            sleep(5)


def run(reddit, model):
    # Make config variables local to work with python formatting
    bot_name = config.bot_name
    bot_name_raw = config.bot_name_raw

    # Time of last comment replied to
    last_utc = 0

    with open("utc.txt", "r") as f:
        # Retrieve the last UTC replied to
        last_utc = f.read().split("\n")[-1]

    try:
        # Search reddit comments for those containing the bot name using Pushshift API
        comment_url = fr"https://api.pushshift.io/reddit/search/comment/?q={bot_name_raw}&sort=desc&size=50&fields=author,body,created_utc,id,subreddit&after=" + last_utc
        parsed_comment_json = json_dump_and_parse("comment_data.json", requests.get(comment_url))

        if (len(parsed_comment_json["data"]) > 0):
            last_utc = parsed_comment_json["data"][0]["created_utc"]

        print ("\nFetching comments..")

        for comment in parsed_comment_json["data"]:

            comment_author = comment["author"]
            comment_body = comment["body"]
            comment_id = comment["id"]
            comment_subreddit = comment["subreddit"]
            comment_reply = ""

            if ((bot_name_raw in comment_body or bot_name in comment_body) and comment_author != bot_name):
                print ("\nFound comment.")
                message = re.search(fr"{bot_name_raw}, (.*)", comment_body, re.IGNORECASE)
                if message:
                    message = message.group(1)
                
                # Generate reply to comment
                comment_reply = generate(input_text=message, model_name=model, length=randrange(80, 160))
                # Remove run on sentence if present
                for i in range(1, len(comment_reply)-1):
                    if comment_reply[-i] in {".", "?", "!"}:
                        comment_reply = comment_reply[:-(i-1)] 
                        break
                # Post generated reply on reddit
                reply_to_comment(reddit, comment_id, comment_reply, comment_subreddit, comment_author, comment_body)
        
        # Remove comment data after bot is done with it
        if os.path.exists("comment_data.json"):
            os.remove("comment_data.json")

    except Exception as e:
        print(str(e.__class__.__name__) + ": " + str(e))

    # Write to file the last utc
    # Commented out for testing
    #with open("utc.txt", "w") as f:
    #   f.write(str(last_utc))

    return str(last_utc)

if __name__ == "__main__":
    reddit = login()
    if len(sys.argv) != 2:
        print('You must enter the model name as a parameter, e.g.: bot.py 355M')
        sys.exit(1)    
    model = sys.argv[1]
    run(reddit, model)
