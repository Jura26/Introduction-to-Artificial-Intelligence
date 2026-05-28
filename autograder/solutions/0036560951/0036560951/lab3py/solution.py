import argparse
import math

parser = argparse.ArgumentParser()

parser.add_argument("train", type=str)
parser.add_argument("test", type=str)
parser.add_argument("depth", type=str, nargs="?", default=None)

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

class ID3:

    def __init__(self, depth=None):
        self.root = None
        self.depth = depth
        self.featuresTrain = None
        self.params = None
        self.decisionSet = None

    @staticmethod
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
                continue
            entropy -= decisionCount[d]/n * math.log(decisionCount[d]/n, 2)
        return entropy

    @staticmethod
    def id3(D, Dparent, params, decisionSet, depth):
        
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
        
        if (depth == 0):
            return Node(isLeaf=True, leafDecision=maxV)
        depth -= 1

        dEntropy = ID3.entropy(D, decisionSet)
        max = -1
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
                entropys[key] = ID3.entropy(value, decisionSet)

            n = len(D)
            ig = dEntropy
            for key, value in Ds.items():
                ig -= len(value)/n * entropys[key]
            
            print(f"IG({p})={ig:.5f}", end=" ")

            if ig > max:
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
        newParams = params.copy()
        newParams.remove(x)

        for key, value in dNext.items():
            t = ID3.id3(value, D, newParams, decisionSet, depth)
            subtrees[key] = t
        ret = Node(x, subtrees, common=maxV)
        return ret
    
    @staticmethod
    def printBranches(node, level, prefix):
        if node.isLeaf == False:
            prefix += f"{level}:{node.param}"
            for key, value in node.next.items():
                childPrefix = f"{prefix}={key} "
                ID3.printBranches(value, level + 1, childPrefix)
        else:
            print(f"{prefix}{node.leafDecision}")

    @staticmethod
    def predictAll(node, currEntry):
        while node.isLeaf == False:
            if currEntry.featureMap[node.param] in node.next:
                node = node.next[currEntry.featureMap[node.param]]
            else:
                return node.common
        return node.leafDecision

    @staticmethod
    def calcMatrix(predictions, decisionSet):
        predictionSet = set()
        for prediction in predictions:
            predictionSet.add(prediction)
        decisionSet = decisionSet | predictionSet
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
            if predictions[i] in decisionMap.keys() and featuresTest[i].decision in decisionMap.keys():
                res[decisionMap[featuresTest[i].decision]][decisionMap[predictions[i]]] += 1
        return res
    
    def fit(self, featuresTrain):
        self.root = ID3.id3(featuresTrain, featuresTrain, params, decisionSet, self.depth)
        print("[BRANCHES]:")
        ID3.printBranches(self.root, 1, "")

    def predict(self, featuresTest):
        print("[PREDICTIONS]:", end=" ")
        correct = 0
        predictions = []
        for currEntry in featuresTest:
            prediction = ID3.predictAll(self.root, currEntry)
            print(prediction, end=" ")
            predictions.append(prediction)
            if prediction == currEntry.decision:
                correct += 1
        print()
        accuracy =correct / len(featuresTest)
        print(f"[ACCURACY]: {accuracy:.5f}")
        print("[CONFUSION_MATRIX]:")
        matrix = ID3.calcMatrix(predictions, decisionSet)
        for i in range(0, len(matrix)):
            for j in range(0, len(matrix)):
                print(matrix[i][j], end=" ")
            print()

if args.depth:
    model = ID3(int(args.depth))
else:
    model = ID3(float('inf'))
model.fit(featuresTrain)
model.predict(featuresTest)