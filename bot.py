# bot.py
# reddit bot that replies to comments invoking it
# Adapted from Harshita Yerramreddy: https://github.com/hyerramreddy/my_friendly_bot/blob/master/bot.py

import os
import sys
import praw
import config
import re
from time import sleep
from random import randrange
from generate import generate
from clean_data import markdown_to_text
import json
import requests


def login():
    reddit = praw.Reddit(client_id=config.client_id,
                         client_secret=config.client_secret,
                         user_agent=f'{config.bot_name} v1.0 by Shaiyon Hariri',
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
    except:
        print("\nCannot reply to comment. moving to next one..")


def run(reddit, model):

    # Time of last comment replied to
    last_utc = 0

    with open("utc.txt", "r") as f:
        # Retrieve the last UTC replied to
        last_utc = f.read().split("\n")[-1]

    try:
        # Search reddit comments for those containing the bot name using Pushshift API
        comment_url = fr"https://api.pushshift.io/reddit/search/comment/?q={config.bot_name_raw}&sort=desc&size=50&fields=author,body,created_utc,id,subreddit&after=" + last_utc
        parsed_comment_json = ""
        try:
            parsed_comment_json = json_dump_and_parse("comment_data.json", requests.get(comment_url))
        except:
            print("Pushshift API is down. Wait until it comes back up. :(")
            sys.exit(1)
        if (len(parsed_comment_json["data"]) > 0):
            last_utc = parsed_comment_json["data"][0]["created_utc"]

        print ("\nFetching comments..")

        for comment in parsed_comment_json["data"]:

            comment_author = comment["author"]
            comment_body = comment["body"]
            comment_id = comment["id"]
            comment_subreddit = comment["subreddit"]
            comment_reply = ""

            if ((config.bot_name_raw in comment_body or config.bot_name in comment_body) and comment_author != config.bot_name):
                print ("\nFound comment.")
                message = re.search(fr"{config.bot_name_raw}, (.*)", comment_body, re.IGNORECASE)
                if message:
                    message = message.group(1)
                    message = markdown_to_text(message)

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
    with open("utc.txt", "w") as f:
        f.write(str(last_utc))


if __name__ == "__main__":
    reddit = login()
    if len(sys.argv) != 2:
        print('You must enter the model name as a parameter, e.g.: bot.py 355M')
        sys.exit(1)    
    model = sys.argv[1]
    run(reddit, model)
