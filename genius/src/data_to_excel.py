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


def data_to_excel(pin, fout):
    fns = glob.glob(pin+'/*/*.json')
    df_proj = []
    df_mem = []
    for fn in fns:
        print('read:', fn)
        obj = json.load(open(fn, 'r'))
        df_proj.append({ 
            'title': obj['title'], 
            'province': obj['province'], 
            'project_id': obj['project_id'], 
            'year': 2000 + int(obj['project_id'][2:4]), 
            'subject': obj['subject'], 
            'category': obj['category'], 
            'key_words': obj['key_words'], 
            'project_desc': obj['project_desc'], 
            'num_members': len(obj['members']), 
            'num_related_images': len(obj['related_images']), 
            'ID': obj['ID'], 
            'award': obj['award'], 
            'list_location': obj['list_location'], 
            'list_category': obj['list_category'], 
            'list_topic': obj['list_topic'], 
            'list_title': obj['list_title']
        })
        for k in range(len(obj['members'])):
            df_mem.append({
                'subject_id': obj['ID'], 
                'project_id': obj['project_id'], 
                'name': obj['members'][k]['name'], 
                'school': obj['members'][k]['school'], 
                'group': obj['members'][k]['group'], 
                'member_index': k, 
            })
    df_proj = pd.DataFrame.from_records(df_proj)
    df_mem = pd.DataFrame.from_records(df_mem)

    with pd.ExcelWriter(fout) as writer:  
        df_proj.to_excel(writer, sheet_name='Project', index=None)
        df_mem.to_excel(writer, sheet_name='Member', index=None)
    return 


if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True, default=None, 
                        help="data path")
    parser.add_argument("-o", "--output", type=str, required=True, default=None, 
                        help="output path of merged data")
    args = parser.parse_args()

    data_to_excel(args.input, args.output)

