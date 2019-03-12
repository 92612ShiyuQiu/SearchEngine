import pymongo
import json
import os
from bs4 import BeautifulSoup
from tokenize import readToken
from collections import defaultdict
import math
import re
from tokenize import countWords
from Tkinter import *
import webbrowser
from stop_words import get_stop_words
import numpy

myclient = pymongo.MongoClient()
mydb = myclient['CS121Proj#3']
mycol = mydb['tokenToDocID']

with open('webpages\\WEBPAGES_RAW\\bookkeeping.json') as f:
    data = json.load(f)

'''
Below is the class I get from the internet for making a scrollbar that can contain buttons in it.
Source: https://gist.github.com/bakineugene/76c8f9bcec5b390e45df
Since my import section is slightly different from his/hers, I made tiny change on his/her code.
'''
class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!

    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)            

        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)
'''
Above is the class I get from the internet for making a scrollbar that can contain buttons in it.
Source: https://gist.github.com/bakineugene/76c8f9bcec5b390e45df
Since my import section is slightly different from his/hers, I made tiny change on his/her code.
'''

def normalize(vector):
    norm = numpy.linalg.norm(vector)
    if norm == 0: 
       return vector
    return vector / norm

def cosineSimilarity(ordered_tokens, common, all_postings):
    query_vector = normalize(getQueryVector(ordered_tokens))
    cosineDict = {}
    for doc in common:
        vector = normalize(getVector(doc, all_postings, ordered_tokens))
        dot = float(numpy.dot(query_vector, vector))
        base = float(numpy.linalg.norm(vector)*numpy.linalg.norm(query_vector))
        cosine = float(dot/base)
        cosineDict[doc] = cosine
    rankedDocs = sorted(list(cosineDict.keys()), key = lambda k: -cosineDict[k])
    for i in rankedDocs[:20]:
        print(i, cosineDict[i])
    return rankedDocs
        
def getVector(docID, all_postings, ordered_tokens):
    vector = []
    for t in ordered_tokens:
        l = [l[1] for l in all_postings[t] if l[0] == docID]
        print(l)
        vector.append(l[0])
        #vector.append([l[1] for l in all_postings[t] if l[0] == docID][0])
    return vector

def getWeightTF(t, ordered_tokens):
    tf = float(float(ordered_tokens.count(t))/float(len(ordered_tokens)))
    if tf > 0:
        weight = 1+math.log(tf, 10)
    else:
        weight = 0
    return weight

def getQueryVector(ordered_tokens):
    queryVector = []
    for t in ordered_tokens:
        tf = getWeightTF(t, ordered_tokens) 
        idf = math.log(float(float(len(ordered_tokens))/float(ordered_tokens.count(t))), math.e)
        tfidf = tf*idf
        queryVector.append(tfidf)
    return queryVector

def overlap1by1(ordered_tokens, all_postings):
    top = ordered_tokens[0]
    common = [l[0] for l in all_postings[top]]
    for i in range(len(ordered_tokens)-1):
        next_top = ordered_tokens[i+1]
        next_posting = all_postings[next_top]
        next_docs = [l[0] for l in next_posting]
        common = list(set(common) & set(next_docs))
    return common

def regetIDF(token, t_postinglist):
    numDocs = float(len(data.keys()))
    numtokenDocs = float(len(t_postinglist))
    return math.log(float(numDocs/numtokenDocs), math.e)

def getOrderedTokens(useful_tokens, all_postings):
    orderedTokens = sorted(list(all_postings.keys()), key = lambda token:len(all_postings[token]))
    return orderedTokens    

def getMultiQueryDocs(useful_tokens):
    all_postings = {}
    for t in useful_tokens:
        myquery = {'token':t}
        t_founddata = mycol.find(myquery)
        for t_found in t_founddata:
            all_postings[t] = t_found['docID']
    orderedTokens = getOrderedTokens(useful_tokens, all_postings)
    common = overlap1by1(orderedTokens, all_postings)
    rankedDocs = cosineSimilarity(orderedTokens, common, all_postings)
    return rankedDocs

def singleQueryDocs(query_tokens):
    print("entered sngleQueryDocs...")
    myquery = {"token":query_tokens[0]}
    print(myquery)
    founddata = mycol.find(myquery)
    print(founddata[0]['docID'][:20])
    mydocID = [i[0] for i in founddata[0]['docID'][:20]]
    return mydocID   

def getUsefulTokens(query_tokens):
    stopwords = get_stop_words('english')
    useful_tokens = []
    for t in query_tokens:
        if t not in stopwords:
            useful_tokens.append(t)
    return useful_tokens

def standarizeQuery(text):
    line = re.sub(r'\W+', " ", text.lower())
    tokens = set(line.split())
    return list(tokens)

def setTKwindow():    
    app = Tk()
    app.title("ShiyuQiu_SearchEngine")
    app.geometry("500x300+200+200")
    labelText = StringVar()
    labelText.set("Query: ")
    label1 = Label(app, textvariable = labelText)
    label1.pack(side="top")
    entryText = StringVar()
    searchBar = Entry(app, textvariable = entryText)
    searchBar.pack(side = 'top', padx=15, pady = 15)
    screenInfo=StringVar()
    
    def search():
        window = Toplevel(app)
        window.geometry("1000x600+200+200")
        label2 = Label(window, textvariable=screenInfo)
        scframe = VerticalScrolledFrame(window)
        scframe.pack(side = RIGHT, fill=Y)
        user_query=searchBar.get()
        query_tokens = standarizeQuery(user_query)
        results = open("url_results.txt", "a")   
        info=''
        try:
            if len(query_tokens)>1:
                useful_tokens = getUsefulTokens(query_tokens)
                mydocID = getMultiQueryDocs(useful_tokens)
            else:
                mydocID = singleQueryDocs(query_tokens)
            if len(mydocID) == 0:
                info = "Sorry, no document are found based on your query..."
                screenInfo.set(info)
                label2.pack(side='top')
            for x in mydocID[:20]:
                key = x.replace("\\", "/")
                url = "http://"+data[key]
                htmlDir = open("webpages/WEBPAGES_RAW/"+key, "r")
                soup = BeautifulSoup(htmlDir, "lxml")
                if soup.title != None and soup.title.string != None:
                    title = soup.title.string
                else:
                    title = 'No Title'
                if len(url)>100:
                    info = title+'\n'+url[:100]+"..."+"\n"
                else:
                    info = title+"\n"+url+"\n"
                def callback(url):
                    webbrowser.open_new_tab(url)
                button = Button(scframe.interior, height = 2, width = 500, relief = FLAT,
                            text=info, command = lambda url = url: webbrowser.open_new_tab(url))
                button.pack( side = 'top')
                results.write("key: "+user_query+"\t"+"url: "+url+"\n")
        except:
            info = "Sorry, no document are found based on your query..."
            screenInfo.set(info)
            label2.pack(side='top')
        results.close()
    button1 = Button(app, text = 'Search', width = 20, command = search)
    button1.pack(side='bottom', padx=15, pady = 15)
    app.mainloop()

if __name__ == "__main__":
    setTKwindow()
