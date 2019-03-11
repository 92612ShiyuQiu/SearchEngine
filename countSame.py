#Shiyu Qiu 22243702
#importing libraries
import sys
from collections import defaultdict
import string
import re
import codecs

#Open the file and readlines. Iterate those lines to process each of them by re.sub
#to get rid of non alphabat characters. Split the line and convert the splited list
#into a set and update into the ftokens set and return the ftokens
#complexity: O(length of content)
def readToken(fileAdd):
    fileopen = codecs.open(fileAdd, "r", 'utf8', errors='ignore')
    content = fileopen.readlines()
    tokens = []
    for line in content:
	line = re.sub(r'\W+', " ", line.lower())
	tokens.extend(line.split())
    ftokens = set(tokens)
    return ftokens

#iterate the first set to make a dictionary
#whose keys are distinct words of the first file
#and whose values are 1
#iterate the distinct words set of the second file to
#make them new keys if they don't exist in the original keys(),
#otherwise just add 1 to the value of that key.
#finally return the len of the list containing keys
#whose values are greater than 0ne
#complexity: O(length of the token set)
def countSame(contentB, contentA):
    count = 0
    Adict = defaultdict(int)
    for w in contentA:
	Adict[w] += 1
    for w in contentB:
	Adict[w] += 1    
    return len([k for k,v in Adict.items() if v>1]) 

if __name__ == "__main__":
    contentA = readToken(sys.argv[1])
    contentB = readToken(sys.argv[2])
    print(countSame(contentB, contentA))
