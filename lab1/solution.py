import argparse
import heapq
from collections import deque

parser = argparse.ArgumentParser()

parser.add_argument("--alg", type=str, nargs="?", default=None)
parser.add_argument("--ss", type=str)
parser.add_argument("--h", type=str, nargs="?", default=None)
parser.add_argument("--check-optimistic", action="store_true")
parser.add_argument("--check-consistent", action="store_true")

args = parser.parse_args()

class Node:
    def __init__(self, distance: float, name: str, prev: "Node" = None):
        self.distance = distance
        self.name = name
        self.prev = prev

    def __str__(self):
        return f"{self.distance}:{self.name}"
    
    def __lt__(self, other):
        return (self.distance, self.name) < (other.distance, other.name)

def fun(s: str):
    name = s.split(", ")[1]
    return float(s.split(", ")[0]) + float(heuristic[name])

def runUCS(start: str):
    open = []
    heapq.heapify(open)
    root = Node(0, start)
    heapq.heappush(open, root)
    finished = set()
    c=0
    while len(open) != 0:
        curr = heapq.heappop(open)

        if curr.name in finished:
            continue
        
        c+=1
        if curr.name in endStates:
            return curr.distance

        for element in nextStates.get(curr.name, []):
            if element.split(",")[0] not in finished:
                distance = float(element.split(",")[1])
                distance = distance + curr.distance
                newNode = Node(distance, element.split(",")[0], curr)
                heapq.heappush(open, newNode)
        finished.add(curr.name)
    return -1


with open(args.ss, "r") as f:
    start = f.readline()
    while start.startswith("#"):
        start = f.readline()
    start = start[:-1]
    end = f.readline()
    while end.startswith("#"):
        end = f.readline()
    endStates = end.split()
    nextStates = {}

    for line in f:
        if line.startswith("#"):
            continue
        
        key = line.split(": ")[0]
        if len(line.split(": ")) == 1:
            continue
        values = line.split(": ")[1]
        valuelist = values.split()
        valuelist.sort()
        nextStates[key] = valuelist

if args.h is not None:
    with open(args.h, "r") as f:
        heuristic = {}
        for line in f:
            el = line.split(": ")
            heuristic[el[0]] = el[1]


if args.alg == "bfs":
    print("# BFS")
    open = deque()
    root = Node(0, start)
    open.append(root)
    finished = set()
    c=0
    while len(open) != 0:
        curr = open.popleft() 

        if curr.name in finished:
            continue
        
        c+=1
        if curr.name in endStates:
            pathlist = []
            root = curr
            while root != None:
                pathlist.append(root.name)
                root = root.prev
            
            print("[FOUND_SOLUTION]: yes")
            print(f"[STATES_VISITED]: {c}")
            print(f"[PATH_LENGTH]: {len(pathlist)}")
            print(f"[TOTAL_COST]: {curr.distance}")
            print(f"[PATH]: ", end="")
            for i in range(len(pathlist)-1,0,-1):
                print(f"{pathlist[i]} => ", end="")
            print(pathlist[0])
            exit(0)

        for element in nextStates.get(curr.name, []):
            if element.split(",")[0] not in finished:
                distance = float(element.split(",")[1])
                distance = distance + curr.distance
                newNode = Node(distance, element.split(",")[0], curr)
                open.append(newNode)
        finished.add(curr.name)
    print("[FOUND SOLUTION]: no")

if args.alg == "ucs":
    print("# UCS")
    open = []
    heapq.heapify(open)
    root = Node(0, start)
    heapq.heappush(open, root)
    finished = set()
    c=0
    while len(open) != 0:
        curr = heapq.heappop(open)

        if curr.name in finished:
            continue
        
        c+=1
        if curr.name in endStates:
            pathlist = []
            root = curr
            while root != None:
                pathlist.append(root.name)
                root = root.prev
            
            print("[FOUND_SOLUTION]: yes")
            print(f"[STATES_VISITED]: {c}")
            print(f"[PATH_LENGTH]: {len(pathlist)}")
            print(f"[TOTAL_COST]: {curr.distance}")
            print(f"[PATH]: ", end="")
            for i in range(len(pathlist)-1,0,-1):
                print(f"{pathlist[i]} => ", end="")
            print(pathlist[0])
            exit(0)

        for element in nextStates.get(curr.name, []):
            if element.split(",")[0] not in finished:
                distance = float(element.split(",")[1])
                distance = distance + curr.distance
                newNode = Node(distance, element.split(",")[0], curr)
                heapq.heappush(open, newNode)
        finished.add(curr.name)
    print("[FOUND SOLUTION]: no")

if args.alg == "astar":
    print(f"# A-STAR {args.h}")
    open = []
    open.append("0, " + start + ", 0")
    finished = []
    c=0
    while len(open) != 0:
        
        c+=1
        if open[0].split(", ")[1] in endStates:
            pathlist = []
            for i in range(0, len(open[0].split(", "))):
                if(i % 3 == 1):
                    pathlist.append(open[0].split(", ")[i])
            
            print("[FOUND_SOLUTION]: yes")
            print(f"[STATES_VISITED]: {c}")
            print(f"[PATH_LENGTH]: {len(pathlist)}")
            print(f"[TOTAL_COST]: {open[0].split(", ")[0]}")
            print(f"[PATH]: ", end="")
            for i in range(len(pathlist)-1,0,-1):
                print(f"{pathlist[i]} => ", end="")
            print(pathlist[0])
            exit(0)

        n = open.pop(0)
        finished.append(n)

        for key, value in nextStates.items():
            if key == n.split(", ")[1]:
                
                for m in value:
                    distance = float(m.split(",")[1]) + float(n.split(", ")[0])
                    found = "None"
                    for el in finished:
                        if(el.split(", ")[1] == m.split(",")[0]):
                            found = el
                            break
                    for el in open:
                        if(el.split(", ")[1] == m.split(",")[0]):
                            found = el
                            break
                    if(found != "None"):
                        if(distance > float(found.split(", ")[0])):
                            continue
                        if found in open:
                            open.remove(found)
                        if found in finished:
                            finished.remove(found)
                    newEl = str(distance) + ", " + m.split(",")[0]
                    newEl = newEl + ", " + str(fun(newEl))
                    open.append(newEl + ", " + n)
        
        open.sort(key=lambda s: (fun(s), s.split(", ")[1]))
    print("[FOUND SOLUTION]: no")
    
if (args.check_consistent):
    print(f"# HEURISTIC-CONSISTENT {args.h}")
    fail = False
    for key, val in sorted(nextStates.items()):
        for value in val:
            print("[CONDITION]:", end=" ")
            if(float(heuristic[key]) <= float(heuristic[value.split(",")[0]]) + float(value.split(",")[1])):
                print("[OK]", end=" ")
            else:
                print("[ERR]", end=" ")
                fail = True
            print(f"h({key}) <= h({value.split(",")[0]}) + c: {float(heuristic[key])} <= {float(heuristic[value.split(",")[0]])} + {float(value.split(",")[1])}")

    if fail == False:
        print("[CONCLUSION]: Heuristic is consistent.")
    else:
        print("[CONCLUSION]: Heuristic is not consistent.")

if (args.check_optimistic):
    print(f"# HEURISTIC-OPTIMISTIC {args.h}")
    fail = False
    for key, value in sorted(heuristic.items()):
        print("[CONDITION]:", end=" ")
        res = float(runUCS(key))
        if float(value) <= res:
            print("[OK]", end=" ")
        else:
            print("[ERR]", end=" ")
            fail = True
        print(f"h({key}) <= h*: {float(heuristic[key])} <= {res}")

    if fail == False:
        print("[CONCLUSION]: Heuristic is optimistic.")
    else:
        print("[CONCLUSION]: Heuristic is not optimistic.")