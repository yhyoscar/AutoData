import json 
import copy
import os
import re
import argparse
import random 
import glob
import time  
import datetime 
import multiprocessing
import numpy as np 
import requests
import selenium
from selenium import webdriver
from bs4 import BeautifulSoup
from multiprocessing import Pool


def download_detail(nprocess = 8):

    #for prefix in ['student_innovation', 'mentor_sciedu', 'student_sciactivity', 'student_creative', 'paint']:
    for prefix in ['student_innovation', ]:

        url_root = "http://castic.xiaoxiaotong.org/Query/"

        pout = prefix
        fpages = sorted(glob.glob(pout+'/awards/'+prefix+'_page*.html'))
        urls = []
        for fpage in fpages:
            soup = BeautifulSoup(open(fpage, 'r'), 'html.parser') 
            for x in soup.find_all('a', class_="item", href=re.compile("ID=")):
                urls.append(url_root+x.attrs['href'])

        print(prefix, 'total pages:', len(urls), ', unique:', len(set(urls)))

        arglist = [(url, pout+'/details/'+url.split('=')[-1], url.split('=')[-1]) for url in urls]
        with multiprocessing.Pool(processes=nprocess) as pool:
            results = pool.starmap(parse_one_url, arglist)

        dout = list(zip(urls, results))
        print('missing: ', [x for x in dout if x[1] not in ['valid', 200]])

    return


def parse_one_url(url, pout, prefix):
    if not os.path.isdir(pout):
        os.system('mkdir -p '+pout)

    if os.path.exists(pout+'/'+prefix+'.json'):
        if open(pout+'/'+prefix+'.json','r').read().strip() == "{}":
            return "empty"
        else:
            return "valid"
    else:
        # max requests: 3 times
        for k in range(3):
            r = requests.get(url)
            if r.status_code == 200:
                break

        obj = dict()
        if r.status_code == 200:
            
            # save to html file as backup
            print('save', url, 'to', pout+'/'+prefix+'.html')
            open(pout+'/'+prefix+'.html', 'wb').write(r.content)
            
            # parse to json file
            soup = BeautifulSoup(r.text, 'html.parser')

            # members
            tmp = soup.find_all('div', class_="mens-photo")[0]
            members = tmp.find_all('div', class_="clearfix")
            obj['members'] = []
            for i in range(len(members)):
                if members[i].img:
                    img_url = members[i].img['src']
                    img_format = os.path.splitext(img_url)[-1]
                    img_local = pout+'/member_'+format(i)+img_format
                    save_img(img_url, img_local)
                    obj['members'].append({'name': members[i].find_all('p', class_="name")[0].text.strip(), 
                        'school': members[i].find_all('p', class_="school")[0].text.strip(),
                        'group': members[i].find_all('p', class_="group")[0].text.strip(), 
                        'image_local': img_local})

            # project information 
            obj['title'] = soup.h1.text 
            td = soup.table.find_all('td')
            obj['province']   = td[0].text
            obj['project_id'] = td[1].text 
            obj['subject']    = td[2].text 
            obj['category']   = td[3].text
            obj['key_words']  = td[4].text
            obj['project_desc'] = soup.find_all('p', class_="xmjj")[0].text.strip() 

            # related images
            obj['related_images'] = []
            all_image = soup.find_all('div', class_="pic")[0].find_all('div', class_="item")
            for i in range(len(all_image)):
                if all_image[i].img:
                    img_url = all_image[i].img['src']
                    img_format = os.path.splitext(img_url)[-1]
                    img_local = pout+'/related_image_'+format(i)+img_format
                    save_img(img_url, img_local)
                    obj['related_images'].append(img_local)
            
            print('save to json file:', pout+'/'+prefix+'.json')
        else:
            print('Error status code in request:', url, ', status:', r.status_code)
        
        json.dump(obj, open(pout+'/'+prefix+'.json', 'w'), indent=2)

        return r.status_code


def save_img(url, fout):
    try: 
        res = requests.get(url)
        if res.status_code == 200:
            print('save image to:', fout)
            open(fout, 'wb').write(res.content)
        else: 
            print('Error status code in request image url:', url, ', status:', res.status_code)
    except:
        print('Error in request image url:', url)



if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--nprocess", type=int, required=False, default=8, 
                        help="number of processes")
    args = parser.parse_args()

    download_detail(nprocess = args.nprocess)


