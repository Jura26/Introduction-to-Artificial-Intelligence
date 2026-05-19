import argparse
import math

parser = argparse.ArgumentParser()

parser.add_argument("train", type=str)
parser.add_argument("test", type=str)
parser.add_argument("alg", type=str, nargs="?", default=None)

args = parser.parse_args()

class entry:
    def __init__(self, features:dict, decision:str):
        self.featureMap = features
        self.decision = decision

class Node:
    def __init__(self, param = None, next = {}, isLeaf = False, leafDecision = None, common = None):
        self.param = param
        self.next = next
        self.isLeaf = isLeaf
        self.leafDecision = leafDecision
        self.common = common

with open(args.train, 'r') as f:
    decisionSet = set()
    params = f.readline().strip().split(",")
    result = params.pop()
    featuresTrain = []
    for line in f:
        lineArr = line.strip().split(",")
        decision = lineArr.pop()
        decisionSet.add(decision)
        featureMap = {}
        for i in range (0,len(lineArr)):
            featureMap[params[i]] = lineArr[i]
        newEntry = entry(featureMap, decision)
        featuresTrain.append(newEntry)

with open(args.test, 'r') as f:
    params = f.readline().strip().split(",")
    params.pop()
    featuresTest = []
    for line in f:
        lineArr = line.strip().split(",")
        decision = lineArr.pop()
        featureMap = {}
        for i in range (0,len(lineArr)):
            featureMap[params[i]] = lineArr[i]
        newEntry = entry(featureMap, decision)
        featuresTest.append(newEntry)

def entropy(D, decisionSet):
    decisionCount = {}
    for d in decisionSet:
        decisionCount[d] = 0
    for currEntry in D:
        decisionCount[currEntry.decision] += 1
    
    n = len(D)
    entropy = 0
    for d in decisionSet:
        if decisionCount[d] == 0:
            return 0
        entropy -= decisionCount[d]/n * math.log(decisionCount[d]/n, 2)
    return entropy

def id3(D, Dparent, params, decisionSet):

    if len(D) == 0:
        decisionCount = {}
        for d in decisionSet:
            decisionCount[d] = 0

        for currEntry in Dparent:
            decisionCount[currEntry.decision] += 1
        
        max = 0
        maxV = None

        for key, value in decisionCount.items():
            if value > max:
                max = value
                maxV = key

        return Node(isLeaf=True, leafDecision=maxV)
    
    decisionCount = {}
    for d in decisionSet:
        decisionCount[d] = 0

    for currEntry in D:
        decisionCount[currEntry.decision] += 1
        
    max = 0
    maxV = None

    for key, value in decisionCount.items():
        if value > max:
            max = value
            maxV = key
        elif value == max:
            if maxV != None and maxV > key:
                max = value
                maxV = key


    if len(params) == 0 or max == len(D):
        return Node(isLeaf=True, leafDecision=maxV)
  
    dEntropy = entropy(D, decisionSet)
    max = 0
    x = None
    
    for p in params:
        
        Ds = {}
        for d in D:
            if d.featureMap[p] in Ds:
                Ds[d.featureMap[p]].append(d)
            else:
                Ds[d.featureMap[p]] = []
                Ds[d.featureMap[p]].append(d)
        entropys = {}
        for key, value in Ds.items():
            entropys[key] = entropy(value, decisionSet)

        n = len(D)
        ig = dEntropy
        for key, value in Ds.items():
            ig -= len(value)/n * entropys[key]
        
        print(f"IG({p})={round(ig, 4)}", end=" ")

        if ig > max:    #sortiranje u ig-u
            x = p
            max = ig
            dNext = Ds
        elif ig == max:
            if x == None or p < x:
                x = p
                max = ig
                dNext = Ds
    
    print()    
    subtrees = {}
    newParams = params
    newParams.remove(x)

    for key, value in dNext.items():
        t = id3(value, D, newParams, decisionSet)
        subtrees[key] = t
    ret = Node(x, subtrees, common=maxV)
    return ret

def printBranches(node, level, prefix):
    if node.isLeaf == False:
        prefix += f"{level}:{node.param}"
        for key, value in node.next.items():
            childPrefix = f"{prefix}={key} "
            printBranches(value, level + 1, childPrefix)
    else:
        print(f"{prefix}{node.leafDecision}")

def predict(node, currEntry):
    while node.isLeaf == False:
        if currEntry.featureMap[node.param] in node.next:
            node = node.next[currEntry.featureMap[node.param]]
        else:
            return node.common
    return node.leafDecision

def calcMatrix(predictions, decisionSet):
    predictionSet = set()
    for prediction in predictions:
        predictionSet.add(prediction)
    decisionSet = decisionSet & predictionSet
    decisionList = sorted(list(decisionSet))
    decisionMap = {}
    for i in range(0, len(decisionList)):
        decisionMap[decisionList[i]] = i
    
    res = []
    for i in range(0, len(decisionList)):
        temp = []
        for j in range(0, len(decisionList)):
            temp.append(0)
        res.append(temp)

    for i in range(0, len(predictions)):
        res[decisionMap[featuresTest[i].decision]][decisionMap[predictions[i]]] += 1
    return res

D = featuresTrain
Dparent = D
root = id3(D, Dparent, params, decisionSet)
print("[BRANCHES]:")
printBranches(root, 1, "")
print("[PREDICTIONS]:", end=" ")
correct = 0
predictions = []
for currEntry in featuresTest:
    prediction = predict(root, currEntry)
    print(prediction, end=" ")
    predictions.append(prediction)
    if prediction == currEntry.decision:
        correct += 1
print()
accuracy =correct / len(featuresTest)
print(f"[ACCURACY]: {round(accuracy, 5)}")
print("[CONFUSION_MATRIX]:")
matrix = calcMatrix(predictions, decisionSet)
for i in range(0, len(matrix)):
    for j in range(0, len(matrix)):
        print(matrix[i][j], end=" ")
    print()




