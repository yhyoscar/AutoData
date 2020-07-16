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
from bs4 import BeautifulSoup
from multiprocessing import Pool


def download_detail(nprocess = 8):
    search_id_range = [0, 90000]

    prefixs = ['student_innovation', 'mentor_sciedu', 'student_sciactivity', 'student_creative', 'paint']
    url_roots = [ 
        "http://castic.xiaoxiaotong.org/Query/SubjectDetail.aspx?SubjectID=", 
        "http://castic.xiaoxiaotong.org/Query/ResultDetail.aspx?ResultID=", 
        "http://castic.xiaoxiaotong.org/Query/ActivityDetail.aspx?ActivityID=", 
        "http://castic.xiaoxiaotong.org/Query/CreativeDetail.aspx?CreativeID=", 
        "http://castic.xiaoxiaotong.org/Query/PaintDetail.aspx?PaintID=" ]

    for k in range(5):
        prefix = prefixs[k]
        url_root = url_roots[k]

        urls = [url_root + format(uid)  for uid in range(search_id_range[0], search_id_range[1])]
        pout = prefix
        
        arglist = [(url, pout+'/'+url.split('=')[-1], url.split('=')[-1]) for url in urls]
        with multiprocessing.Pool(processes=nprocess) as pool:
            pool.starmap(parse_one_url, arglist)

    return


def parse_one_url(url, pout, prefix):
    if not os.path.isdir(pout):
        os.system('mkdir -p '+pout)

    if not os.path.exists(pout+'/'+prefix+'.html'):
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
            if len(members) > 0:
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

    return 


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