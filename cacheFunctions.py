from utils import *

### Global variables
nodeFrequencyList = [[] for i in range(32)]
meansForIntervals = []
frequencyDict = dict()


def queryFrequencies(queries):
    global frequencyDict
    for query in queries:
        for term in Tokenizer.tokenize(query, stem=False):
            if term in frequencyDict.keys():
                frequencyDict[term] += 1
            else:
                frequencyDict[term] = 1
    #sort dictionary by value
    sortedDic = dict(sorted(frequencyDict.items(), key=lambda x: x[1], reverse=True))
    #print first 10 item in the dictionary
    return sortedDic

def everyNodeFrequency(termMap):

    global nodeFrequencyList
    for term in termMap.keys():
        nodeID = termMap[term]
        if term in frequencyDict.keys():
            nodeFrequencyList[nodeID].append([term,[ frequencyDict[term],[] ] ] )
    for i in range(32):
        nodeFrequencyList[i] =  sorted(nodeFrequencyList[i], key=lambda x: x[1], reverse=True)
    
    # return nodeFrequencyList

## If period is 16 and interval is 8, then we will have 2 hours each interval
def queryFrequencyStability(tPeriod, tInterval, queries, timeStamps):
    global meansForIntervals
    dic = dict()
    i=-1
    intervalHours = tPeriod/tInterval
    lenTimeStamps = len(timeStamps)
    firstTS = timeStamps[0]
    lastTS = timeStamps[-1]
    diffTS = lastTS - firstTS
    newIntervalTS = int(diffTS/tInterval)+1
    counter = 1

    for query in queries:
        i+=1
        
        if(timeStamps[i] > counter*(newIntervalTS)+firstTS or i == lenTimeStamps-1):
            # print(counter*(newIntervalTS)+firstTS)
            # intervalHours+= tPeriod/tInterval
            #sort dictionary by value
            
            if(i == lenTimeStamps-1):
                for term in Tokenizer.tokenize(query, stem=False):
                    if term  in dic:
                        dic[term] += 1
                    else:
                        dic[term] = 1

            sortedDic = sorted(dic.items(), key=lambda x: x[1], reverse=True)
            meansForIntervals.append( dict(sortedDic))
            dic = dict()

            if(int(counter*(newIntervalTS)) > diffTS or i == lenTimeStamps-1):
                print('if breaked')
                break
            counter += 1

            

        for term in Tokenizer.tokenize(query, stem=False):
            if term  in dic:
                dic[term] += 1
            else:
                dic[term] = 1


def findQFS(inputTerm):
    totalF = 0
    frequencyOfTerm = []
    for freqDicStability in meansForIntervals:
        
        if(inputTerm not in freqDicStability.keys()):
            totalF += 0
            frequencyOfTerm.append(0)
        else:
            totalF += freqDicStability[inputTerm]
            frequencyOfTerm.append(freqDicStability[inputTerm])

    meanForTerm = totalF/len(meansForIntervals)
    QFStability = 0

    for i in frequencyOfTerm:
        QFStability += (abs(i - meanForTerm))/meanForTerm
    
    # print('inputTerm===>',inputTerm, ',,,QFStability===>',QFStability*totalF, ',,,meanForTerm===>',meanForTerm, ',,,frequencyOfTerm===>',frequencyOfTerm)
    
    return(QFStability*totalF)

def stabilityFunction(termMap):
    tPeriod =16
    tInterval = 8
    # queryFrequencyStability(tPeriod,tInterval)

    global nodeFrequencyList
    for term in termMap.keys():
        nodeID = termMap[term]
        if term in frequencyDict.keys():
            nodeFrequencyList[nodeID].append([term,[ findQFS(term),[] ] ] )
    for i in range(32):
        nodeFrequencyList[i] =  sorted(nodeFrequencyList[i], key=lambda x: x[1], reverse=True)

def findNewQF(inputTerm):
    totalF = 0
    frequencyOfTerm = []
    for i in meansForIntervals:
        totalF += i[inputTerm]
        frequencyOfTerm.append(i[inputTerm])

    meanForTerm = totalF/len(meansForIntervals)
    QFStability = 0
    for i in frequencyOfTerm:
        QFStability += (abs(i - meanForTerm))/meanForTerm

    print(QFStability)
