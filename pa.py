### Written by Derin Karadeniz, on Sunday, 18 December 2022

from configFile import *
from utils import compareBM25List
from utils import splitQueryAndTime
from utils import Tokenizer
import utils
from node import Node
import math

docLengthsDictionary = utils.docLengthsDictionary
docDic = utils.docDic

### CONFIGS
partitioningType = PartitioningType.TERMBASED
partitionNum = 32
wordListFileName = 'wordlist.txt'
queryListFileName = '10000.topics'
### 

### GLOBALS
cumulativeDic = {}
documentDict = {}
###
#Reads the binary file and prints the entries

def docLengths():
    global docLengthsDictionary
    with open('doc_lengths.txt') as f:
        lines = f.readlines()
        for line in lines:
            line = line.split(' ')
            docLengthsDictionary[line[0]] = line[1]
            

def readBinaryFile():
    global docDic
    k = 0
    with open('entry.bin', 'rb') as f:
        # data = f.seek(8*seekLength)
        for (key,(startPos,pll)) in cumulativeDic.items():
            data = (f.read(pll*8).hex(':', 4)).split(':')
            # k+=1
            # if(k==1000):
            #     break
            j = 0
            docId = -1
            docDic[key]= {}
            for i in data:
                newData = bytearray.fromhex(i)[::-1].hex(':',4)
                if(j%2 == 0):
                    docId = int(newData, 16)
                else:
                    docDic[key][docId] = int(newData, 16)
                j+=1

    # return docDic



def wordListReader(filename):
    wordList = []

    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=' ')
        for row in csv_reader:
            wordList.append(row)
    
    return wordList


def queryListReader(filename):
    queryList = []

    with open(filename, encoding='latin1') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=':')
        for row in csv_reader:
            querylistRow = row[1].translate(str.maketrans('','',string.punctuation))
            queryList.append(querylistRow.split(' '))
    
    return queryList


def termBasedPartitioner(wordList, partitionNum): 
    partitionDictList = []
    for i in range(partitionNum):
        newDict = dict()
        partitionDictList.append(newDict)
    termMap = {}
    
    cumulativeArr = [0]
    global cumulativeDic
    cumulativeDic = {}

    listIndex = 0
    while listIndex < len(wordList):
        partitionIndex = listIndex % partitionNum
        partitionDictList[partitionIndex][wordList[listIndex][0]] = wordList[listIndex][1]
        termMap[wordList[listIndex][0]] = partitionIndex

        cumulativeDic[wordList[listIndex][0]] = (cumulativeArr[-1], int(wordList[listIndex][1]))
        cumulativeArr.append(cumulativeArr[-1]+int(wordList[listIndex][1]))

        listIndex = listIndex + 1

    return partitionDictList, termMap, cumulativeDic


def documentBasedPartitioner(wordList, partitionNum):
    partitionDict = {}
    termMap = {}

    listIndex = 0
    while listIndex < len(wordList):
        partitionDict[wordList[listIndex][0]] = wordList[listIndex][1]
        listIndex = listIndex + 1
    
    partitionDictList = partitionNum * [partitionDict]

    return partitionDictList, termMap


def pseudoPartition(partitionDict, query):
    totalCost = 0
    minCost = sys.maxsize

    for term in query:
        PLL = partitionDict.get(term)
        if PLL is not None:
            PLL = float(PLL)
            if PLL > 0:
                totalCost = totalCost + PLL
                minCost = min(minCost, PLL)
    
    if minCost == sys.maxsize:
        minCost = 0

    return totalCost, minCost


def broker(query, nodeList, termMap):
    totalCost = 0
    partitionCostList = []
    totalPartitionCost = 0
    minPartitionCost = sys.maxsize

    nodeTermList = [[] for _ in range(len(nodeList))]

    for term in query:
        # NOTE: Check starting termMap Value index. 0 or 1
        if term in termMap.keys():
            nodeTermList[termMap[term]].append(term) 

    # print('nodeList',nodeList)
    print('nodeTermList',nodeTermList)

    nodeTopKDocList = []
    partitionIndex = 0
    for node in nodeList:
        if len(nodeTermList[partitionIndex]) != 0:
            nodeTopKDoc = node.calculateTopKDoc(nodeTermList[partitionIndex])
            nodeTopKDocList.append(nodeTopKDoc)
            # print('nodeTopKDoc', nodeTopKDoc)

        totalCost = totalCost + minPartitionCost
        partitionCostList.append(totalPartitionCost)
        partitionIndex = partitionIndex + 1
    
    topKDoc = compareBM25List(nodeTopKDocList)
    
    return topKDoc, totalCost, partitionCostList


def main():
    wordList = wordListReader(wordListFileName)
    queryList,_ = splitQueryAndTime()
    nodeList = []
    global cumulativeDic
    if partitioningType.value == PartitioningType.TERMBASED.value:
        partitioner = termBasedPartitioner
    else:
        partitioner = documentBasedPartitioner
    
    [partitionDictList, termMap, cumulativeDic] = partitioner(wordList, partitionNum)
    docLengths()
    readBinaryFile()
    for nodeNum in range(partitionNum):
        nodeList.append(Node(partitionDictList[nodeNum]))

    queryIndex = 0
    brokerCost = 0
    partitioncCostList = len(partitionDictList) * [0] ####
    for query in queryList:
        print('before tokenizer',query)
        newQuery = []
        newQuery = Tokenizer.tokenize(query)
        print('after tokenizer= =', newQuery)
        newQuery = ['year', 'old']
        [topKDoc, currBrokerCost, currPartitionCostList] = broker(newQuery, nodeList, termMap)
        brokerCost = brokerCost + currBrokerCost
        partitioncCostList = list(map(add, partitioncCostList, currPartitionCostList))
        queryIndex = queryIndex + 1
        print('topKDoc',topKDoc)
        
        exit(0)
    brokerCost = brokerCost / queryIndex
    partitioncCostList[:] = [x / queryIndex for x in partitioncCostList]
    overallCost = brokerCost + max(partitioncCostList)

    f = open("results.txt", "a")
    now = datetime.datetime.now()
    f.write(f'Execution Date Time: {now.strftime("%Y-%m-%d %H:%M:%S")}\n')
    f.write(f'Partitioning Type: {partitioningType.name}\n')
    f.write(f'Partition Num: {partitionNum}\n')
    f.write(f'Average Broker Cost: {brokerCost}\n')
    f.write(f'Average Partition Costs: {partitioncCostList}\n')
    f.write(f'Overall Cost: {overallCost}\n\n')
    f.close()
    return 0

if __name__ == "__main__":
    main()