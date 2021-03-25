"""
Download Amazon jobs information

example usage: 
python3 download_with_requests.py -o [output csv file to restore the data]
"""

import json 
import copy
import sys
import os
import re
import argparse
import random 
import time  
import datetime 
import multiprocessing
import numpy as np 
import pandas as pd 
import requests
from bs4 import BeautifulSoup



def download_joblist(search_text, fout):
    if os.path.dirname(fout) not in ['.', './', '/', '']:
        os.system('mkdir -p '+os.path.dirname(fout))
    
    urls = get_url_list(search_text)
    print(urls)

    return 

    
    
def get_url_list(search_text):
    urls = []
    jobs_per_page = 10
    html_text = get_one_page("https://www.amazon.jobs/en/search?offset=0&sort=recent&base_query="+search_text+"&country=USA")
    if html_text != '':
        soup = BeautifulSoup(html_text, 'lxml')
        obj = soup.find("div", class_="job-count-info")
        if obj is not None:
            njob = int(obj.text.strip().split(' ')[-2])
        else:
            njob = 0
        
        #print('njob:', obj.text)
        if njob > 0:
            for ipage in range(int(np.ceil(njob/jobs_per_page))):
                urls.append("https://www.amazon.jobs/en/search?offset="+format(ipage*jobs_per_page)+"&sort=recent&base_query="+search_text+"&country=USA")
    return urls

    
def get_one_page(url):
    print(url)
    i = 0
    for headers in json.load(open('headers.json', 'r')):
        # try:
        print(headers)
        res = requests.get(url, headers=headers, timeout=10, allow_redirects=False)
        if res.status_code == 200:
            open('tmp'+format(i)+'.html', 'w').write(res.text)
            i+=1
            #return res.text
        else:
            print('Error: failed in get, status_code =', res.status_code)
            #return ''
        # except:
        #     print('Error: Connection issue')
        #     return ''
    return ''

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search_text", type=str, required=True, default=None, 
                        help="search text")
    parser.add_argument("-o", "--output", type=str, required=True, default=None, 
                        help="output csv file to restore the downloaded data")
    args = parser.parse_args()

    download_joblist(args.search_text.strip('"').strip().replace(' ', '%20'), args.output)

