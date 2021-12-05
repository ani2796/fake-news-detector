import logging
from typing import OrderedDict
import requests
import pandas as pd
from bs4 import BeautifulSoup
from newspaper import fulltext, Article
import json
import re
import time

def json_to_obj(filename):
    """Extracts data from JSON file and saves it on Python object
    """
    obj = None
    with open(filename) as json_file:
        obj = json.loads(json_file.read())
    return obj

def make_login(session, base_url, credentials):
    """Returns a Session object logged in with credentials.
    """
    login_form_url = '/login/device-based/regular/login/?refsrc=https%3A'\
        '%2F%2Fmobile.facebook.com%2Flogin%2Fdevice-based%2Fedit-user%2F&lwv=100'

    params = {'email':credentials['email'], 'pass':credentials['pass']}

    while True:
        time.sleep(3)
        logged_request = session.post(base_url+login_form_url, data=params)
        
        if logged_request.ok:
            logging.info('[*] Logged in.')
            break

def get_bs(session, url):
    """Makes a GET requests using the given Session object
    and returns a BeautifulSoup object.
    """
    r = None
    while True:
        r = session.get(url)
        time.sleep(1)
        if r.ok:
            break
    return BeautifulSoup(r.text, 'lxml')

def scrape_post(session, base_url, post_id):
    """Goes to post URL and extracts post data.
    """
    post_data = {}

    post_url = "/" + str(post_id)
    final_url = base_url + post_url

    post_bs = get_bs(session, final_url)

    for link in post_bs.find_all('a'):
            url = link.get('href')
            try:
                matching_url = re.search(".*lm.facebook.*", url)
            except:
                print("Cannot find link for article, moving on to the next one...")
                return
            if(matching_url):
                post_data = {
                    "id": post_id,
                    "link": matching_url.string,
                    "html": get_bs(session, matching_url.string)
                }
                post_data["js"] = post_data["html"].find('script', type='text/javascript').string
                actual_url = re.search('\".*\"', post_data["js"]).group(0).replace("\"", "").replace("\\", "")
                post_data["actual_url"] = actual_url
                break
    return post_data



if __name__ == "__main__":
    facebook_data = pd.read_csv("../facebook-fact-check.csv")
    fields = ['post_id', 'Category', 'Page', 'Post URL', 'Date Published', 'Post Type', 'Rating']
    facebook_data = facebook_data[fields]
    facebook_data = facebook_data.rename(columns = {'post_id':'id', 'Category':'category', 'Post URL':'url', 'Page':'source', 'Date Published':'date', 'Post Type':'type', 'Rating':'TF'})
    facebook_data = facebook_data[facebook_data['type'] == 'link']
    facebook_data["Title"] = ""
    facebook_data["Text"] = ""

    logging.basicConfig(level=logging.INFO)
    base_url = 'https://mobile.facebook.com'
    session = requests.session()

    # Note that you will have to change the credentials_sample.json to credentials.json for this line to work
    
    credentials = json_to_obj('credentials.json')
    make_login(session, base_url, credentials)

    for idx, row in facebook_data.iterrows():
        post_id = row['id']
        link = row['url']

        # Check the link below for further work:
        # https://python.gotrained.com/scraping-facebook-posts-comments/

        # Quick ref to dataset:
        # https://github.com/BuzzFeedNews/2016-10-facebook-fact-check/blob/master/data/facebook-fact-check.csv

        # Using the newspaper library
        # https://github.com/codelucas/newspaper?ref=pythonrepo.com

        # Some dataframes help/cheat sheet:
        # https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf

    print(str(facebook_data.head()))

    row_count = len(facebook_data.index)
    print("Row count: " + str(row_count))

    for i in range(row_count):
        post_info = facebook_data.iloc[i]
        post_id = post_info['id']
        post_url = post_info['url']
        
        print("Test link: " + str(post_url))
        post_hyperlink = scrape_post(session, base_url, str(post_id))

        if post_hyperlink and "id" in post_hyperlink:
            print("Retreiving link successful!")
            print("Details: " + str(post_hyperlink["link"]))
            url = post_hyperlink["actual_url"]
            print("Actual link: " + url)
            article = Article(url)
            try:
                article.download()
                article.parse()
                facebook_data.iat[i, facebook_data.columns.get_loc('Title')] = article.title
                facebook_data.iat[i, facebook_data.columns.get_loc('Text')] = article.text.replace("-- ", "")
            except:
                print("Link doesn't work any more, moving on...")
        else:
            print("Invalid link, so sadge...")
        print("\n")
    
    facebook_data.to_csv("extracted_data.csv")