#!/usr/bin/env python
# coding: utf-8

# In[9]:


### Import Libaries
### Modules needed for NLP
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import itertools
import collections
import json
import tweepy as tw
import nltk
from nltk import bigrams
from nltk.corpus import stopwords
import re
import networkx as nx
import warnings
from textblob import TextBlob
#Kaggle API modules
import subprocess
import glob
from kaggle.api.kaggle_api_extended import KaggleApi


warnings.filterwarnings("ignore")

sns.set(font_scale=1.5)
sns.set_style("whitegrid")


# In[10]:


#Authorize API's
#Authorize Twitter API
f = open('/home/pi/twitter_api_creds.json')
creds = json.load(f)
consumer_key = creds['consumer_key']
consumer_secret = creds['consumer_secret']
access_token = creds['access_token']
access_token_secret = creds['access_token_secret']
f.close()

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)
#Authorize Kaggle's API
kapi = KaggleApi()
kapi.authenticate()


# In[11]:


#Twitter Functions
#Calls on clean() for text cleanup then removes the URL
def remove_url(txt):
    #Call on clean to clean text first
    txt = clean(txt)
    #removes URL
    return " ".join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", txt).split())

#Cleans up the text like newlines before url is removed.
def clean(text):
    
    # removing paragraph numbers
    text = re.sub('[0-9]+.\t','',str(text))
    # removing new line characters
    text = re.sub('\n ','',str(text))
    text = re.sub('\n',' ',str(text))
    # removing apostrophes
    text = re.sub("'s",'',str(text))
    # removing hyphens
    text = re.sub("-",' ',str(text))
    text = re.sub("— ",'',str(text))
    # removing quotation marks
    text = re.sub('\"','',str(text))
    # removing salutations
    text = re.sub("Mr\.",'Mr',str(text))
    text = re.sub("Mrs\.",'Mrs',str(text))
    # removing any reference to outside text
    text = re.sub("[\(\[].*?[\)\]]", "", str(text))
    
    return text


# In[22]:


#Twitter functions
#Returns DF of list of cleaned tweets for sentiment analysis
#Calls on clean_url() in above block to clean and remove URL
#Takes in user inputs as parameters to search for tweets
#Can also be used alone if the terms are hardcoded; for testing
def extract_tweets_configed(search_term, opt, num, date_ans, lower = False):
    tweets = tw.Cursor(api.search,
                   q=search_term,
                   lang="en",
                   since=date_ans).items(num)
    # Remove URLs by calling on functions in block above
    tweets_no_urls = [remove_url(tweet.text) for tweet in tweets]
    # Create textblob objects of the tweets
    sentiment_objects = [TextBlob(tweet) for tweet in tweets_no_urls]
    # Get sentiment values
    sentiment_values = [[tweet.sentiment.polarity, str(tweet)] for tweet in sentiment_objects]
    #put into dataframe
    sentiment_df = pd.DataFrame(sentiment_values, index = None, columns=["polarity", "tweet"])
    #remove neutral sentiment values
    #sentiment_df = sentiment_df[sentiment_df.polarity != 0]
    return sentiment_df
#Gets the user inputs to pass to extract_tweets_configed
#Prompts for search term, retweet filter option, num to extract and date since.
def user_inputs():
    # Valid final string ex. "#climate+change -filter:retweets"
    print("Enter tweet search term(s): ")
    print("E.g. ''#climatechange' should be entered as: #climate+change")
    search_term = input()
    #Prompt for retweet filter
    opt = input("Filter out retweets? Enter as y/n: ")
    if (opt == 'y'):
        search_term = search_term + " -filter:retweets"
    #prompt for number of tweets to be extracted    
    num = input("How many tweets to be extracted? Enter as int: ")
    num = int(num)
    #prompt for date since in YYYY-MM-DD or default to '2018-11-01'
    date = '2018-11-01'
    date_ans = input("Since what date? Enter as: YYYY-MM-DD or 'n' for default of 2018-11-01: ")
    if (date_ans == 'n'):
        date_ans = date
    df = extract_tweets_configed(search_term, opt, num, date_ans)
    return df
#Calls on user_inputs and returns a cleaned dataframe of tweets ready for sentiment analysis.
def extract_tweets():
    return user_inputs()


# In[26]:


df = extract_tweets()

# search_term = "#climate+change -filter:retweets"
# opt = "y"
# num = 100
# date = "2018-11-01"
# df = extract_tweets_configed(search_term, opt, num, date)

df = df[df.polarity != 0]
#df.head()


# In[24]:


#Update this to be full process to be scaled
#Save df as a csv locally for later upload to kaggle
# loc = '/home/pi/kaggle_data_analysis_project/upload_stage'
# name = '/home/pi/kaggle_data_analysis_project/upload_stage/out.csv'
loc = input("Enter directory path where datasets will be locally: ")
name = input("Enter file name, do NOT include .csv: ")
name = loc + '/' + name + '.csv'
df.to_csv(name, index = False)
# df.head()


# In[25]:


# Setting up checks for needing to init, create,
# or simply update a version
search_for_init = 'dataset-metadata.json'
public = False
owd = '/home/pi/kaggle_data_analysis_project'
os.chdir(loc)
meta_exists = glob.glob('./*.json')

if(len(meta_exists) == 0): #if true no json exists
    kapi.dataset_initialize(loc)
    print("Set up initialization .JSON in directory to proceed.")
    
#if status is 'ready' then data set exists
#if status is None, then create a new dataset
status = kapi.dataset_status("emrejakbulut/twitter-sentiment-dataset")
if(status == None):
    print("Check dataset name, if trying to update existing and rerun this block ")
    pub = input("Make dataset(s) public? Enter y/n: ")
    if(pub == 'y'):
        public = True
    kapi.dataset_create_new(loc, public=public)
    
if(status == 'ready'):
    #keeps old versions by default
    kapi.dataset_create_version(loc, "updated", delete_old_versions = False)


# In[22]:


#Upload to kaggle
# Initialize the directory, only once
#kapi.dataset_initialize(loc) #add in logic using ls *.json
#Use this command when making first version
# kapi.dataset_create_new(loc)
#kapi.dataset_create_version(loc, "updated", delete_old_versions = False)

