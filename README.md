# SubredditBot
Have you ever found yourself needing a third party to intervene in a reddit argument? Do you need answers to seemingly unanswerable questions? Maybe you're just bored and wouldn't mind a neural network buddy to chat with. In that case, SubredditBot is for you!

## Abstract

This project is a reddit bot that generates coherent, humorous responses to a user prompt when invoked. For text generation, it employs the state of the art GPT-2 language model developed by OpenAI with tensorflow, fine-tuned with reddit comment data from any set of subreddits desired. Using Python, I cleaned the comment data for modeling, and am currently adjusting model hyperparameters and code for optimum generation. Additionally, I will develop a bot that responds to any comment starting with "WatchBot, " in the /r/Watches subreddit, using the text after the comma as a prompt the bot uses to generate a random amount of text (1-3 paragraphs) in response.

## Motivation

I remember first being captivated by GPT-2 while watching [Computerphile's YouTube video on a sample it generated](https://www.youtube.com/watch?v=89A4jGvaaKk). How can nothing but statistical relationships between words generate such robust and coherent text? I was extremely excited when I found out the code was released to the public, and wanted to try using it myself. I hypothesized that reddit comments would be the perfect data source to fine-tune the model, as there is a never-ending sea of comments available with interesting content. Thus, SubredditBot was born.

## Methodology - the data

The reddit comment data was collected from [Google BigQuery's public database](https://bigquery.cloud.google.com/dataset/fh-bigquery:reddit_comments), containing comments from as far back as 2005. An SQL query was enough to gather the text needed:
```sql
#legacySQL
SELECT 
  body
FROM 
  TABLE_QUERY([fh-bigquery:reddit_comments], "REGEXP_MATCH(table_id, '^201._..$')"),
  TABLE_QUERY([fh-bigquery:reddit_comments], "REGEXP_MATCH(table_id, '^20..$')")
WHERE
  subreddit IN ("Watches", "WatchHorology", "WatchesCirclejerk", "Seiko", "rolex", "Tudor", 
  "OmegaWatches", "casio", "pocketwatch", "clocks", "gshock", "smartwatch")
```
I'm a huge watch geek, so I chose watch related subreddits, but this query can be successfuly run with any group of subreddits.


The result of the query was a massive 505MB csv of text:

body |
------------ |
"My \[GMT Master II BLNR\]\(http://i.imgur.com/thisisalink.jpg) and I, driving around town on battery power."|
"[deleted]"|
"Close! It's act grade 2 titanium (grade 2 will darken and develop a patina over time and I can tell its a little bit darker than when I got it back in late June) and 18k rose gold. \n\nThanks, it's really a neat color scheme that they got going on with this particular Speedmaster that you don't see everyday. "  |
"\&gt; Adding on to that I think that having a seconds hand is pointless if it is not showing the actual correct second.\n\nIt's really not that pointless. It gives you a quick way to check if your watch is actually still running and it also allows you to time things. I use it for the latter quite often. \n\nI don't think it's that silly since watches are marketed as luxury goods now, and not really as time keeping devices."|
"I will go ahead and not believe that whatsoever, while you go ahead and try to make another claim saying you are actually not a trust fund baby."|

The data is clearly high quality, but is in the markdown format and needs to be cleaned up before encoding and feeding into GPT-2. Code and more detail on the data cleaning process can be found [here](../master/clean_data.ipynb).

## Methodology - the model

GPT-2 needs no introduction, and neither does its incredible ability to generate semi-lifelike text samples multiple paragraphs long. Projects like [AI Dungeon 2](https://towardsdatascience.com/the-creator-of-ai-dungeon-2-shares-gpt-2-finetuning-advice-e5800df407c9) have proven the model's viability in providing the user interacting with it a lot of entertainment. With Python and Tensorflow, I finetuned the 355 million hyperparameter edition of the model, as larger ones refused to load into my GPU's memory. Code for finetuning and text generating [here](../master/train_model.py).  

Here are a few early stage samples:

>"My only concern is that that they are only about $70 and I am not an expert on Seiko. I have been wearing them through college and high school and it is still in great shape."

>"The thing is a bit old, but it looks really nice. I bought it from the 70s and had no complaints about it. They've been out of stock on eBay for a while, but I guess they're back now due to demand from buyers?"

>"However, the dials on your sub are just stunning! (I had my eye on one from the 1970s. That is the style that I currently wear on a daily basis.)"

The samples sound slightly off (the model really likes the number 70), but nothing a bit of hyperparameter tuning can't fix! My next step is to more strongly deincentivize repetition so the temperature can be lowered, and tweaking the optimizer / learning rate.

## Methodology - the bot

>IN PROGRESS

## This README and project are still under construction. A lot more coming soon.
