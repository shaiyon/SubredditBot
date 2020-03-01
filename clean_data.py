# clean_data.py
# preprocess reddit comments for modeling
# Shaiyon Hariri

import re
import sys
from csv import QUOTE_NONE
import pandas as pd
from bs4 import BeautifulSoup
from markdown import markdown

# Pass in name of dataset as system argument
if len(sys.argv) != 2:
    print('You must enter the dataset file name as a parameter, e.g.: clean_data.py comments.csv')
    sys.exit(1)

# Use iloc to make Series
# Can use any subreddit dataset(s).
try:
    data = pd.read_csv(sys.argv[1]).iloc[:,1]
    print("Data loaded. cleaning...")
except:
    print("Data failed to load. Make sure the dataset is in the same directory as the script.")
    sys.exit(1)

# Remove NaN values and empty strings
data.dropna(inplace=True)
# Remove deleted comments
data = data.loc[data != "[deleted]"]
# Filter out bots and sale posts
data = data[~data.str.contains("^", regex=False)]
data = data[~data.str.contains("|", regex=False)]
# Remove entries too small for dataset
data = data[data.str.len() > 30]
data = data.str.replace(r'\n{1,}', ' ', regex=True)

def markdown_to_text(markdown_string):
    """ Converts a markdown string to plaintext """

    # md -> html -> text since BeautifulSoup can extract text cleanly
    html = markdown(markdown_string)

    # Remove code snippets
    html = re.sub(r'<pre>(.*?)</pre>', ' ', html)
    html = re.sub(r'<code>(.*?)</code >', ' ', html)

    # Extract text
    soup = BeautifulSoup(html, "html.parser")
    text = ''.join(soup.findAll(text=True))
    text = ''.join(c for c in text if ord(c) < 128)
    
    return text


# Transform markdown reddit comments to plaintext
data = data.apply(markdown_to_text)
# Remove legacy JSON and other unwanted characters
data = data.str.replace('&amp;', '&', regex=False).str.replace('&lt;', '<', regex=False).str.replace('&gt;', '>', regex=False).str.replace('&#x200B;' , ' ', regex=False)
# Remove entries with links and URLs (they distort the data)
data = data.str.replace(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', regex=True)
# Remove entries too small for dataset (again)
data = data[data.str.len() > 30]
# Remove whitespace at beginning and end
data = data.str.strip()
# Drop duplicates and reset index
data.drop_duplicates(inplace=True)
data.reset_index(drop=True, inplace=True)

# Save cleaned data
print("Data cleaned. saving...")
saved_file_name = sys.argv[1][:-4] + "_cleaned.txt"
data.to_csv(saved_file_name, sep='\n', index=False, header=False, quoting=QUOTE_NONE, quotechar="", escapechar="\n")
print("Data saved.")
