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
import selenium
from selenium import webdriver


def parse_url(search_text, levels, offset):
    return f"https://amazon.jobs/en/internal/search?offset={offset}&refine_facet=Tech%20Jobs&&base_query="+search_text.replace(' ', '%20')+''.join([f'&job_level[]={level}' for level in levels])

def download_search_results(search_texts=["Applied Scientist"], levels=[4,5], nprocess=2):

    #driver = webdriver.Firefox()
    
    jobs = []
    for search_text in search_texts:
        driver = webdriver.Chrome()
        npage = get_page_count(driver, parse_url(search_text, levels, 0))
        print('search text: ', search_text, ', npage:', npage)
        driver.close()
                
        urls = [parse_url(search_text, levels, i*10) for i in range(npage)]

        if nprocess > 1:
            arglist = [(urls[i::nprocess], ) for i in range(nprocess)]
            with multiprocessing.Pool(processes=nprocess) as pool:
                outs = pool.starmap(one_process_get_urls, arglist)
            jobs += sum(outs, [])
        else:
            jobs += one_process_get_urls(urls)

    fout = 'search_results_'+datetime.datetime.now().isoformat()[:19]+'.csv'
    df = pd.DataFrame.from_records(jobs)
    df = df.drop_duplicates(subset=['ID'])
    df['posted'] = pd.to_datetime(df['posted'])
    df = df.sort_values('posted', ascending=False)
    print('save job list to:', fout, len(df))
    df.to_csv(fout, index=None)

    return 


def one_process_get_urls(urls):
    driver = webdriver.Chrome()
    outs = []
    for url in urls:
        print('get job list from:', url)
        outs += get_job_list(driver, url)
    driver.close()
    return outs


def get_page_count(driver, url, request=True):
    if request: driver.get(url)
    driver.get(url)
    pages = get_elements(driver, 'page-button', by='class')
    return int(pages[-1].text)


def get_job_list(driver, url, request=True):
    if request: driver.get(url)
    joblist = get_elements(driver, 'job-link', by='class')
    while len(joblist) == 0:
        joblist = get_elements(driver, 'job-link', by='class')
        time.sleep(0.1)

    jobs = []
    for job in joblist:
        locid = job.find_element_by_class_name('location-and-id').text.strip()
        dt = job.find_element_by_class_name('posting-and-start-date').text
        obj = { #'nowtime': datetime.datetime.now().isoformat(), 
            'link': job.get_property("href"), 
            'title': job.find_element_by_class_name('job-title').text.strip(), 
            'location': locid.split('|')[0].strip(), 
            'ID': locid.strip().split(' ')[-1], 
            'posted': dt.split('.')[0].split(':')[-1].strip(), 
            'updated': dt.split('.')[-1].split(':')[-1].strip(), 
            'short-description': job.find_element_by_class_name('description').text, 
            'hiring-manager': job.find_element_by_class_name('hiring-manager').text.strip(), 
            'deparment': job.find_element_by_class_name('department').text.strip(), 
            }
        jobs.append(obj)
    return jobs


def get_one_element(obj, key, by='class', timeout=5):
    finish = False
    element = None
    t0 = time.time()
    while (not finish) and (time.time()-t0 < timeout): 
        try:
            if by=='class': element = obj.find_element_by_class_name(key)
            if by=='id': element = obj.find_element_by_id(key)
            if by=='tag': element = obj.find_element_by_tag_name(key)
            if by=='name': element = obj.find_element_by_name(key)
            if element:
                finish = True
        except:
            finish = False
        time.sleep(0.1)
    return element

def get_elements(obj, key, by='class', timeout=5):
    finish = False
    es = []
    t0 = time.time()
    while (not finish) and (time.time()-t0 < timeout): 
        try:
            if by=='class': es = obj.find_elements_by_class_name(key)
            if by=='id': es = obj.find_elements_by_id(key)
            if by=='tag': es = obj.find_elements_by_tag_name(key)
            if by=='name': es = obj.find_elements_by_name(key)
            if es:
                finish = True
        except:
            finish = False
        time.sleep(0.1)
    return es


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search", type=str, required=True, default=None, 
                        help="key_word1,key_word2,...")
    parser.add_argument("-l", "--level", type=str, required=False, default='4,5', 
                        help="level1,level2,...")
    parser.add_argument("-n", "--nprocess", type=int, required=False, default=2, 
                        help="nprocess")
    args = parser.parse_args()

    download_search_results([x.replace('_', ' ') for x in args.search.split(',')], 
        [int(level) for level in args.level.split(',')], int(args.nprocess))


