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


def merge_data(phtml, pdetail, pout, nprocess = 8):
    if not os.path.isdir(pout): os.system('mkdir -p '+pout)

    awards = get_award_info(glob.glob(phtml+'/*.html'))
    print(phtml, 'listed awards:', len(awards))

    # valid IDs
    sids = [os.path.basename(fn)[:-5] for fn in glob.glob(pdetail+'/*/*.json') if open(fn,'r').read().strip() != "{}"] 

    print('valid IDs:', len(sids))   

    arglist = [(pdetail, pout, sid, awards) for sid in sids]
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
    parser.add_argument("-p", "--pages", type=str, required=True, default=None, 
                        help="path of html pages with award information")
    parser.add_argument("-d", "--details", type=str, required=True, default=None, 
                        help="path of details data")
    parser.add_argument("-o", "--output", type=str, required=True, default=None, 
                        help="output path of merged data")
    parser.add_argument("-n", "--nprocess", type=int, required=False, default=8, 
                        help="number of processes")
    args = parser.parse_args()

    merge_data(args.pages, args.details, args.output, nprocess = args.nprocess)

