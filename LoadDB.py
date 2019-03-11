import pymongo
import json
import os
from bs4 import BeautifulSoup
import countSame
from tokenize import readToken
from collections import defaultdict
import math
import re
from tokenize import countWords
from Tkinter import *
import webbrowser

rootdir = 'webpages\WEBPAGES_RAW'
subdirs = os.walk(rootdir)

if  os.path.exists("content.txt"):
    os.remove("content.txt")
if  os.path.exists("halfway.txt"):
    os.remove("halfway.txt")
if  os.path.exists("url_results.txt"):
    os.remove("url_results.txt")
if  os.path.exists("table.txt"):
    os.remove("table.txt")
myclient = pymongo.MongoClient()
mydb = myclient["CS121Proj#3"]
collist = mydb.list_collection_names()
if "tokenToDocID" in collist:
    mydb.drop_collection('tokenToDocID')
mycol = mydb['tokenToDocID']
rootdir = 'webpages\WEBPAGES_RAW'
subdirs = os.walk(rootdir)


with open('webpages\\WEBPAGES_RAW\\bookkeeping.json') as f:
    data = json.load(f)

def getHtmlDirsDocIDs():
    htmlDirs = []
    docIDs = []
    for subdir, dirs, files in subdirs:
        preDocID = subdir.split('\\')[-1] 
        for f in files:
            d = os.path.join(subdir, f)
            docID = os.path.join(preDocID, f)
            if ".json" not in d and ".tsv" not in d:
                htmlDirs.append(d)
                docIDs.append(docID)
    return [docIDs, htmlDirs]

def tokenizeString(text):
    line = re.sub(r'\W+', " ", text.lower())
    tokens = line.split()
    return tokens    

def getPreindex():
    preindex = defaultdict(lambda:{"token":str, "docID":[]})
    htmlANDdocs = getHtmlDirsDocIDs()
    htmlDirs = htmlANDdocs[1]
    docIDs = htmlANDdocs[0]
    countB = 0
        
    for f in htmlDirs:
        print(countB)
        countB -= 1
        openf = open(f, 'r').read()
        soup = BeautifulSoup(openf, 'lxml')
        if soup.body != None:
            text = soup.body.text.encode('utf-8').lower()
        else:
            text = ''
        subtokens = tokenizeString(text)
        subtokens_set = set(subtokens)
        countMap = countWords(subtokens)
        for t in subtokens_set:
            tf = getWeightTF(countMap, t, subtokens)
            preindex[t]['token'] = t
            preindex[t]['docID'].append([docIDs[htmlDirs.index(f)],tf])
    for t in preindex:
        idf = getIDF(t, preindex,htmlDirs)
        postingList = preindex[t]['docID']
        for l in postingList:
            tf = l[1]
            l[1] = tf*idf
        preindex[t]['docID'].sort(key=lambda x: -x[1])
        if (t=="informatics"):
            print(preindex[t]['docID'])
    return preindex

def getWeightTF(countMap, t, subtokens):
    tf = float(float(countMap[t])/float(len(subtokens)))
    if tf > 0:
        weight = 1+math.log(tf, 10)
    else:
        weight = 0
    return weight

def printPreindex(num):
    for i in range(0,num):
        print("token:"+preindex[i]['token']+'\t'+"docID:"+preindex[i]['docID']+"\t"+'forRank:'+preindex[i]['forRank']+'\n')
        
def getIDF(token, preindex, htmlDirs):
    numDocs = float(len(htmlDirs))
    numtokenDocs = float(len(preindex[token]['docID']))
    return math.log(float((numDocs/numtokenDocs)), 10)

def insert():
    preindex = getPreindex()
    insertion = list(preindex.values())
    mycol.insert_many(insertion)

if __name__ == '__main__':
    insert()
