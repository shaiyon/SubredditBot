# SubredditBot
Have you ever found yourself needing a third party to intervene in a reddit argument? Do you need answers to seemingly unanswerable questions? Maybe you're just bored and wouldn't mind a neural network buddy to chat with. In that case, SubredditBot is for you!

## Abstract

This project is a reddit bot that generates coherent, humorous responses to a user prompt when invoked. For text generation, it 
deploys the state of the art [GPT-2](https://openai.com/blog/better-language-models/) language model, fine-tuned with reddit comment data from a set of subreddits to mimic the cadence of redditors. I wrote a script to clean and encode reddit comment data for modeling, and adjusted the model's hyperparameters for optimum generation. Additionally, I developed a bot that replies to any comment on reddit containing its name, using the text in the comment as the prompt for generation. All of the code is modular, and replicating my results is very easy!

## Motivation

I remember first being captivated by GPT-2 while watching [Computerphile's YouTube video on a sample it generated](https://www.youtube.com/watch?v=89A4jGvaaKk). How can nothing but statistical relationships between words generate such robust and coherent text? I was extremely excited when I found out the code was released to the public, and wanted to try using it myself. I hypothesized that reddit comments would be the perfect data source to fine-tune the model, as there is a never-ending sea of comments available with interesting content. Furthermore, projects like [AI Dungeon 2](https://towardsdatascience.com/the-creator-of-ai-dungeon-2-shares-gpt-2-finetuning-advice-e5800df407c9) have proven the model's viability in providing the user interacting with it a lot of entertainment. With all the pieces in place, SubredditBot was born.

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


The result of the query was a massive 530MB csv of text:

body |
------------ |
"My \[GMT Master II BLNR\]\(http://i.imgur.com/thisisalink.jpg) and I, driving around town on battery power."|
"[deleted]"|
"Close! It's act grade 2 titanium (grade 2 will darken and develop a patina over time and I can tell its a little bit darker than when I got it back in late June) and 18k rose gold. \n\nThanks, it's really a neat color scheme that they got going on with this particular Speedmaster that you don't see everyday. "  |
"\&gt; Adding on to that I think that having a seconds hand is pointless if it is not showing the actual correct second.\n\nIt's really not that pointless. It gives you a quick way to check if your watch is actually still running and it also allows you to time things. I use it for the latter quite often. \n\nI don't think it's that silly since watches are marketed as luxury goods now, and not really as time keeping devices."|

The data is clearly high quality, but is in the markdown format and needs to be cleaned up before encoding and feeding into GPT-2. Data cleaning script can be found [here](../master/clean_data.py).

## Methodology - the model

GPT-2 (Generative Pretrained Transformer) may be some of the latest and greatest in text generation, but the architecture of the model is not especially novel. It is an extremely large [transformer](https://arxiv.org/abs/1706.03762) pretrained unsupervised on a monstrous 40GB text corpus. Transformers employ a generic mechanism based on encoder-decoders to detect dependencies between inputs and outputs. Due to transformers' property of improving performance linearly when given more data and the large initial dataset, GPT-2 generates text of unprecedented realism. Out of the box, the model is generalized and unspecific, but is ripe for fine-tuning with other data, and the generated text maintains its coherence even after retraining.

<p align="center">
  <img src="https://miro.medium.com/max/1474/1*b15IvFFUT-WtPRdxsnoMQw.png" width="460" height="460"> 
</p>

I fine-tuned the 355 million parameter edition of the model, tweaking hyperparameters to make the text generated seem more natural and less repetitive. Then, I edited an existing script for generating samples to be able to connect with the reddit bot. Code for generating samples [here](../master/interactive_conditional_samples.py).  

## Methodology - the bot

Conveniently, reddit has the functional and easy to use PRAW API, making it relatively painless to develop a bot to suit your needs. The bot searches through all reddit comments created since its last runtime for those containing its name in the format "bot_name, " with the Pushshift API, uses the text after the comma as the prompt for generation, and replies to the initial comment with the text it generated. Bot code [here](../master/bot.py).

Sample interaction with the bot:

watches_bot, Should I buy a Seiko 5?

> Or a Timex Weekender? I'm pretty sure it's just a little bit bigger than a Seiko 5. Wearing my favourite watch this morning as well, the Seiko SNN231. Some of the comments were more supportive of the watch, but I've seen it a lot more than a normal post on here. My wrist is 6.5" and I think it's too big for me, but my general rule is "if you like it, get it." This is my Seiko 5. It's on a perlon strap, I'd say about 6.5" and it's a great watch. It's a little bit smaller than I'd like, but it's pretty much perfect for me. I just got it a few weeks ago, but I haven't worn it much, and I've had it for like 6 months, so I'd like to get back into watches again. I think this is a great collection of watches. It's great to see so many different styles and colors. Not just the new limited edition. The limited edition on this watch was last year. My love for the Citizen Nighthawk has been growing over the last couple years. I had the opportunity to purchase it recently and I fell in love with it. I finally took the plunge and bought it. I know a lot of people are going to be offended by this post, but I wanted to share it with you guys so we all know what a beautiful watch it is. I have a picture of the movement and inside of the caseback. As far as I know, the Nighthawk is the first Citizen I have owned. I have been looking for a watch for a long time and this was the best one I could find for a reasonable price. It came in like a month ago and I've already received a few compliments on it. I think it looks like the regular, just the "battery" I have the same problem with my current watch. I've been trying to figure out what's the best way to tell the time. It's so hard to read the time in the dark. I've never seen a Zim watch with a screw-down crown. That's just so nice to see a Citizen with a chronograph, they usually only have one or two, and I think Citizen's are amazing. I have the same one, and it's also in my daily rotation. I think it's pretty cool, and the

## Key Results

## Summary 

## Future Work



## This README and project are still under construction. A lot more coming soon.
