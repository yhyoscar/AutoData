import json 
import copy
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


directions = [ 
    { 
        'prefix': 'student_innovation', 
        'url': "http://castic.xiaoxiaotong.org/Query/StudentQuery.aspx", 
        "pages": list(range(1, 327)), 
    }, 
    {
        'prefix': "mentor_sciedu", 
        'url': "http://castic.xiaoxiaotong.org/Query/ResultQuery.aspx", 
        'pages': list(range(1, 161)), 
    }, 
    {
        'prefix': "student_sciactivity", 
        'url': "http://castic.xiaoxiaotong.org/Query/ActivityQuery.aspx", 
        'pages': list(range(1, 272)), 
    }, 
    {
        'prefix': "student_creative", 
        'url': "http://castic.xiaoxiaotong.org/Query/CreativeQuery.aspx", 
        'pages': list(range(1, 109)), 
    }, 
    {
        'prefix': "paint", 
        'url': "http://castic.xiaoxiaotong.org/Query/PaintQuery.aspx", 
        'pages': list(range(1, 789)), 
    }
]


def download_list(nprocess = 4):
    # run twice to make sure no missing pages
    for k in range(2):
        for direction in directions:
            prefix = direction['prefix']
            url = direction['url']
            pages = direction['pages']
            print('download list of', prefix, len(pages), 'pages')

            pout = prefix
            if not os.path.isdir(pout):
                os.system('mkdir -p '+pout)

            np.random.shuffle(pages)
            arglist = [(url, pages[i::nprocess], pout, prefix) for i in range(nprocess)]
            with multiprocessing.Pool(processes=nprocess) as pool:
                pool.starmap(one_process, arglist)
    
    return 


def one_process(url, pages, pout, prefix):
    driver = webdriver.Chrome()
    initial = True
    for page in pages:
        fout = pout + "/" + prefix+'_page'+format(page, '03') + '.html'
        if not os.path.exists(fout):
            save_one_page(driver, url, page, fout, initial)
            initial = False
    driver.close()
    return 


def save_one_page(driver, url, page, fout, initial_get=True):
    if initial_get:
        print('get url:', url)
        driver.get(url)
    else:
        print('get page:', page)
        script = "javascript:__doPostBack('AspNetPager1','"+format(page)+"')"
        driver.execute_script(script)
    print('save html to:', fout)
    open(fout, 'w').write(driver.page_source)
    return 



if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--nprocess", type=int, required=False, default=4, 
                        help="number of processes")
    args = parser.parse_args()

    download_list(args.nprocess)


