from utils import *
from utils import BM25Algorithm
from utils import compareBM25List

class Node:
    def __init__(self, nodeTermDict):
        self.Cache = {}
        self.EmptyCacheSize = 10000
        self.NodeTermDict = nodeTermDict
        self.QueryTermList = []
        self.TopKDoc = []
        self.cacheHitCounter = 0
        self.totalRecievedTerm = 0

    def checkCache(self, term):
        isHit = False
        topKBM25 = []
        self.totalRecievedTerm += 1

        if term in self.Cache.keys():
            isHit = True
            topKBM25 = self.Cache.get(term)[1]
            self.cacheHitCounter += 1
            
        return isHit, topKBM25

    def calculateTopKDoc(self, nodeTermList):
        k = 100
        self.TopKDoc = []
        listPL = []
        listBM25 = []

        for term in nodeTermList:
            [isHit, cachedBM25List] = self.checkCache(term) 

            if isHit:
                # print('cacheHit')
                listBM25.append(cachedBM25List)
            else:
                # print('cacheMiss')
                resultBm25 = BM25Algorithm(term)
                # print(resultBm25)
                # print('resultBm25', resultBm25)
                listBM25.append(resultBm25)

        # print('listBM25',listBM25)
        topKDoc = compareBM25List(listBM25)

        return topKDoc