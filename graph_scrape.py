'''
graph_scrape.py

Script for scraping photo captions from a website, as part of the first 
miniproject for the Data Incubator.  

Author: Phillip Schafer (phillip.baker.schafer@mg.thedataincubator.com)
Date: April 11, 2015

Usage:
>> python graph_scrape.py
'''
import pickle
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
from collections import namedtuple
import re
from datetime import datetime
from itertools import chain

def get_index_urls():
    '''  
    Make a list of the index page urls.  The first page is specified by
    `url_stub`.  subsequent pages have `?page=X` appended, where X is an
    integer from 1 to 24. 
    '''
    url_stub = 'http://www.newyorksocialdiary.com/party-pictures'
    index_urls = [url_stub]
    for x in range(1,25):
        index_urls.append(url_stub + '?page=' + str(x))
    return index_urls

def get_album_urls(index_url):
    '''
    From a single index page, scrape out all the urls corresponding
    to an album before Dec 1, 2014.  
    '''
    # load the page
    r = requests.get(index_url)
    soup = BeautifulSoup(r.text)

    # select the chunk of html corresponding to each album listing
    album_divs = soup.select('div.view-content > div')

    # function for getting the url and year from this html chunk 
    AlbumInfo = namedtuple('AlbumInfo', 'date, url')
    def get_info(ad):
        # get year and date html
        l_date = ad.select('span.views-field-created > span')
        l_url = ad.select('span.views-field-title > span > a')
        if len(l_url)!=1 or len(l_date)!=1:
            print 'DID SOMETHING WRONG!!!'
            return None
        
        # extract year and date and return
        date = datetime.strptime(l_date[0].text, '%A, %B %d, %Y')
        url = l_url[0]['href']
        return AlbumInfo(date=date, url=url)
            
    album_infos = [get_info(ad) for ad in album_divs]

    refdate = datetime(2014, 12, 1) # Dec 1, 2014
    return [ai.url for ai in album_infos if ai.date<refdate]
  
def get_captions(url):
    '''
    From a single web album, scrape the captions of all the photos. 
    '''
    url_base = 'http://www.newyorksocialdiary.com'
    r = requests.get(url_base + url)
    soup = BeautifulSoup(r.text)

    caption_divs = soup.select('div.photocaption')
    caption_divs.extend(soup.select('td.photocaption'))
    return [cd.text for cd in caption_divs]
  
  
def main():
    index_urls = get_index_urls()

    album_urls = []
    for iu in index_urls:
        album_urls.extend(get_album_urls(iu))
    print 'total urls: ' + str(len(album_urls))

    workers = Pool(30)
    album_captions = workers.map(get_captions, album_urls)

    # Flatten the list
    captions = list(chain.from_iterable(album_captions)) 
    print 'total captions: ' + str(len(captions))

    pickle.dump(captions, open('captions.p', 'wb'))
  
if __name__ == '__main__':
    main()