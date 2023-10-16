import math 
from nltk.stem.porter import PorterStemmer
import re

docDic = {}
docLengthsDictionary = {}

def BM25Algorithm(term, k1=1.2, b=0.75):
    # b is the parameter for length normalization2
    # k1 is the parameter for term frequency normalization
    # N is the total number of documents
    # avgdl is the average document length
    # query is the query
    # docLength is the length of each document
    global docDic
    global docLengthsDictionary
    N = 210158
    avgdl = 407.941354 
    score = {}
    termPLDic = docDic[term]
    lenPL = len(termPLDic)

    idf = math.log((N - lenPL + 0.5) / ( lenPL + 0.5))
    for doc in termPLDic.keys():
        if doc not in score:
            score[doc] = 0
        tf = termPLDic[doc]

        score[doc] += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * float(docLengthsDictionary[str(doc)]) / avgdl))
    
    Doc_BM_List = []
    for key,value in score.items():
        Doc_BM_List.append((key,value))
    return Doc_BM_List

def compareBM25List(listBM25):
        sumBM25Dict = {}
        listSize = len(listBM25)

        for listNum in range(listSize):
            for currTuple in listBM25[listNum]:
                currTerm = currTuple[0]

                sumBM25 = 0
                if currTerm not in sumBM25Dict.keys():
                    sumBM25 = currTuple[1]

                    searchListBM25 = listBM25[listNum + 1:]

                    for nextList in searchListBM25:
                        foundTuple = tuple(Tuple for Tuple in nextList if Tuple[0] == currTerm)
                        if foundTuple:
                            sumBM25 += foundTuple[0][1]
                    
                    sumBM25Dict[currTerm] = sumBM25

        topBM25 = sorted(sumBM25Dict.items(), key=lambda x:x[1], reverse=True)

        return topBM25


class Tokenizer(object):
  # Standard stop words used by Lucene/Elasticsearch
    STOP_WORDS = [
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 
        'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 
        'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 
        'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 
        'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 
        'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 
        'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 
        'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'com', 'gov', 'edu',
        'www', 'co', 'st', 'net'
    ]

    @staticmethod
    def tokenize(text, toLower=True, removeStopWords=True, stem=False, requireAlpha=False):
        if toLower:
            text = text.lower()

        tokens = text.split()

        if removeStopWords:
            tokens = [x for x in tokens if x.lower() not in Tokenizer.STOP_WORDS]

        if stem:
            stemmer = PorterStemmer()
            tokens = [stemmer.stem(x) for x in tokens]

        if requireAlpha:
            tokens = [x for x in tokens if re.match(r"^[a-z]+$", x.lower())]

        return tokens

def splitQueryAndTime():
    with open('query_log_100K.txt') as f:
        data = f.readlines()
    data = [x.split('==') for x in data]
    queries = [x[1].strip() for x in data]

    timeStamps = [x[0].strip() for x in data]
    timeStamps = [x.split('_') for x in timeStamps]
    timeStamps = [x[1] for x in timeStamps]
    timeStamps = [x.split(':') for x in timeStamps]
    timeStamps = [int(x[0])*3600 + int(x[1])*60 + int(x[2]) for x in timeStamps]
    return queries, timeStamps


def queryFrequencies(num):
    dic = dict()
    queries, _ = splitQueryAndTime()
    for query in queries:
        for term in Tokenizer.tokenize(query, stem=False):
            if term in dic:
                dic[term] += 1
            else:
                dic[term] = 1
    #sort dictionary by value
    sortedDic = dict(sorted(dic.items(), key=lambda x: x[1], reverse=True))
    #print first 10 item in the dictionary
    return(sortedDic.keys()[0:num])