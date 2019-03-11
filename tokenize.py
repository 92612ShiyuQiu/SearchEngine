#Shiyuch flavors of Linux have you installed and why? Qiu 22243702
#importing libraries
import sys
from collections import defaultdict
import re
import string
import codecs

#Open the file and readlines, and iterate lines to process each line to get rid of non alphabat
#characters using re.sub(), and split the result and add to the tokens list.  
#complexity: O(length of content)
def readToken(fileAdd):    
    fileopen = codecs.open(fileAdd, 'r','utf8', errors='ignore')
    content = fileopen.readlines()
    tokens = []
    for line in content:
	line = re.sub(r'\W+', " ", line.lower())
	tokens.extend(line.split())
    return tokens

#create a defaultdict with value of key
#loop the list of tokens and count the number of appearance of each tokens
#and let the token be the key and the number be the value
#complexity: O(length of the token list)
def countWords(tokens):
    countMap = defaultdict(int)
    for t in tokens:
        countMap[t]+=1
    return countMap

#print the counted result in sorted order
#complexity: O(nLogn) (n = number of distinct words)
def show(countMap):
    for key, value in sorted(countMap.iteritems(), key = lambda(key,value):(-value,key)):
        print"%s\t%s" % (key, value)

if __name__ == "__main__":
    tokens = readToken(sys.argv[1])
    countMap = countWords(tokens)
    show(countMap)

