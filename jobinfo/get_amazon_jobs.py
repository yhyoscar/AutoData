"""
Download Amazon jobs information

example usage: 
python3 get_amazon_jobs.py -o [output directory to restore the data]
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
import selenium
from selenium import webdriver


def download_amazon_jobs(pdata):
    if not os.path.isdir(pdata):
        os.system('mkdir -p '+pdata)

    #driver = webdriver.Firefox()
    driver = webdriver.Chrome()
    nprocess = 2

    # get locations in US 
    url = 'https://www.amazon.jobs/en/locations/?&continent=north_america&cache'
    driver.get(url)
    all_loc = driver.find_elements_by_class_name('image-container')
    valid_loc = [loc.get_attribute('id') for loc in all_loc if loc.is_displayed()]
    
    for jobloc in valid_loc:
        if not os.path.exists(pdata+'/'+jobloc+'.json'):
            print('======= download job list at location:', jobloc, '=======')
            url = "https://www.amazon.jobs/en/locations/"+jobloc+"?offset=0&sort=recent&job_type=Full-Time"
            njob = get_job_count(driver, url)
            print('location: ', jobloc, ', job count:', njob)
            
            if njob > 0:
                npage = int(np.ceil(njob/10))
                urls = ["https://www.amazon.jobs/en/locations/"+jobloc+"?offset="+format(int(i*10))+"&sort=recent&job_type=Full-Time" for i in range(npage)]

                arglist = [(urls[i::nprocess], ) for i in range(nprocess)]
                with multiprocessing.Pool(processes=nprocess) as pool:
                    jobs = pool.starmap(one_process_get_urls, arglist)
                jobs = sum(jobs, [])

                print('save job list to:', pdata+'/'+jobloc+'.json')
                json.dump(jobs, open(pdata+'/'+jobloc+'.json', 'w'), indent=2)

    driver.close()
    return 


def one_process_get_urls(urls):
    driver = webdriver.Chrome()
    outs = []
    for url in urls:
        print('get job list from:', url)
        outs += get_job_list(driver, url)
    driver.close()
    return outs


def get_job_count(driver, url, request=True):
    if request: driver.get(url)
    driver.get(url)
    jobcount = get_one_element(driver, 'job-count-info', by='class')
    if jobcount:
        return int(re.findall("of.*?jobs", jobcount.text)[0].split(' ')[1])
    else:
        return 0


def get_job_list(driver, url, request=True):
    if request: driver.get(url)
    joblist = get_elements(driver, 'job-link', by='class')
    while len(joblist) == 0:
        joblist = get_elements(driver, 'job-link', by='class')
        time.sleep(0.1)

    jobs = []
    for job in joblist:
        locid = job.find_element_by_class_name('location-and-id').text 
        obj = {'nowtime': datetime.datetime.now().isoformat(), 
            'href': job.get_property("href"), 
            'title': job.find_element_by_class_name('job-title').text, 
            'location': locid.split('|')[0].strip(), 
            'ID': locid.strip().split(' ')[-1], 
            'posted': job.find_element_by_class_name('posting-date').text.lstrip('Posted').strip(), 
            'updated': job.find_element_by_class_name('time-elapsed').text.lstrip('(Updated').rstrip(')').strip(), 
            'short-description': job.find_element_by_class_name('description').text, 
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
            if by=='name': obj.find_element_by_name(key)
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
            finish = True
        except:
            finish = False
        time.sleep(0.1)
    return es


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", type=str, required=True, default=None, 
                        help="directory to restore the downloaded data")

    args = parser.parse_args()

    download_amazon_jobs(args.output)
