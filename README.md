Project will be about the sentiment of the UN's sustainable development goals before and after covid. 
To answer the question if covid has changed people's attitudes towards seeing the need for a better world. 
https://www.un.org/sustainabledevelopment/sustainable-development-goals/

Uses Twitter's API to extract tweets. Code here can upload the tweets with polarity to google sheets or kaggle, via their API's. Both are free. If trying to replicate this, I would advise getting the script to upload to the dataset to kaggle first.

When uploading to kaggle it will be in a csv format. This can be helpful for producing datasets to use for later. Kaggle does go off and produce graphs on it's own as well. I am still somewhat new to kaggle, but am using it to share datasets and eventually publish results there. 



The other opt does the same but it then uploads a dataframe to Google Sheets,
via the google sheets API. Will be eventually set up to update hourly with crontab by running the scripts. Sheets graphs can change based on new data. 

Written in Jupyter Notebook with Python3, both Notebook and Python3 scripts can be found here.
Sheet link here:
https://docs.google.com/spreadsheets/d/1YLnWNTjsHNhGe65tKdrU_8VRqsAVQmPy4hbqYWpWltw/edit#gid=245284386

Kaggle link here:
https://www.kaggle.com/emrejakbulut/twitter-sentiment-dataset

This is in beta version.
