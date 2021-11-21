import logging
from typing import OrderedDict
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time

if __name__ == "__main__":
    facebook_data = pd.read_csv("../facebook-fact-check.csv")
    fields = ['post_id', 'Category', 'Page', 'Post URL', 'Date Published', 'Post Type', 'Rating']
    facebook_data = facebook_data[fields]
    facebook_data = facebook_data.rename(columns = {'post_id':'id', 'Category':'category', 'Post URL':'url', 'Page':'source', 'Date Published':'date', 'Post Type':'type', 'Rating':'TF'})
    facebook_data = facebook_data[facebook_data['type'] == 'link']

    logging.basicConfig(level=logging.INFO)
    base_url = 'https://mobile.facebook.com'
    session = requests.session()

    for idx, row in facebook_data.iterrows():
        post_id = row['id']
        link = row['url']
        
        # Check the link below for further work:
        # https://python.gotrained.com/scraping-facebook-posts-comments/

        # Quick ref to dataset:
        # https://github.com/BuzzFeedNews/2016-10-facebook-fact-check/blob/master/data/facebook-fact-check.csv

    print(str(facebook_data.head()))

