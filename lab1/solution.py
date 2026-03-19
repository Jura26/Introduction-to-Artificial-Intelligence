import argparse

parser = argparse.ArgumentParser()

parser.add_argument("alg", type=str)
parser.add_argument("ss", type=str)
parser.add_argument("h", type=str, nargs="?", default=None)
parser.add_argument("check-optimistic", type=str, nargs="?", default=None)
parser.add_argument("check-consistent", type=str, nargs="?", default=None)

args = parser.parse_args()

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

if args.alg == "bfs":
    print("# BFS")
    open = []
    open.append("0, " + start + ", 0")
    finished = []
    c=0
    while len(open) != 0:
        
        c+=1
        if open[0].split(", ")[1] in endStates:
            print("[FOUND_SOLUTION]: yes")
            print(f"[STATES_VISITED]: {c}")
            print(f"[PATH_LENGTH]: {int(float(open[0].split(", ")[2])) + 1}")
            print(f"[TOTAL_COST]: {open[0].split(", ")[0]}")
            print(f"[PATH]: ", end="")
            pathlist = []
            for i in range(0, len(open[0].split(", "))):
                if(i % 3 == 1):
                    pathlist.append(open[0].split(", ")[i])
            
            for i in range(len(pathlist)-1,0,-1):
                print(f"{pathlist[i]} => ", end="")
            print(pathlist[0])
            exit(0)

        for key, value in nextStates.items():
            if key == open[0].split(", ")[1]:
                for element in value:
                    if element.split(",")[0] not in finished:
                        distance = float(element.split(",")[1])
                        distance = distance + float(open[0].split(", ")[0])
                        open.append(f"{distance}, {element.split(",")[0]}, {float(open[0].split(", ")[2]) + 1}, {open[0]}")
        finished.append(open[0].split(", ")[1])
        open.remove(open[0])
        open.sort(key=lambda s: (s.split(", ")[1], s.split(", ")[0]))
    print("[FOUND SOLUTION]: no")