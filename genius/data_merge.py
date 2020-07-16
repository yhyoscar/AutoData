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
import pandas as pd 
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool


def merge_data(nprocess = 8):
    prefix = "student_innovation"
    pin = "./"+prefix
    pout = "./clean_data/"+prefix
    if not os.path.isdir(pout): os.system('mkdir -p '+pout)

    awards = get_award_info(glob.glob(pin+'/awards/*.html'))
    print(prefix, 'listed awards:', len(awards))

    # valid IDs
    sids = [os.path.basename(fn)[:-5] for fn in glob.glob(pin+'/details/*/*.json') if open(fn,'r').read().strip() != "{}"]    

    arglist = [(pin+'/details', pout, sid, awards) for sid in sids]
    with multiprocessing.Pool(processes=nprocess) as pool:
        pool.starmap(insert_award_info, arglist)

    return 



def get_award_info(fhtmls):
    objs = dict()
    for fhtml in fhtmls:
        soup = BeautifulSoup(open(fhtml, 'r'), 'html.parser') 
        for x in soup.find_all('a', class_="item", href=re.compile("ID=")):
            objs[x['href'].split('=')[-1]] = { 
                'award': x.find_all('em')[1].text, 
                'list_location': x.find_all('em')[0].text, 
                'list_category': x.find_all('em')[2].text, 
                'list_topic': x.i.text, 
                'list_title': x.span.text, 
             } 
    return objs    


def insert_award_info(pold, pnew, sid, awards):
    fjson = pnew+'/'+sid+'/'+sid+'.json'
    if not os.path.exists(fjson):
        os.system('cp -r '+pold+'/'+sid+' '+pnew)
    obj = json.load(open(fjson, 'r'))
    if len(obj) > 0:
        if 'num_member' in obj: obj.pop('num_member')
        obj['ID'] = sid 
        if sid in awards:
            obj['award'] = awards[sid]['award']
            obj['list_location'] = awards[sid]['list_location']
            obj['list_category'] = awards[sid]['list_category']
            obj['list_topic'] = awards[sid]['list_topic']
            obj['list_title'] = awards[sid]['list_title']
        else:
            obj['award'] = ''
            obj['list_location'] = ''
            obj['list_category'] = ''
            obj['list_topic'] = ''
            obj['list_title'] = ''
        print('rewrite json file:', fjson)
        json.dump(obj, open(fjson, 'w'), indent=2)
    return 


if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--nprocess", type=int, required=False, default=8, 
                        help="number of processes")
    args = parser.parse_args()

    merge_data(nprocess = args.nprocess)

