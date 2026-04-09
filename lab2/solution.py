import argparse
parser = argparse.ArgumentParser()

parser.add_argument("alg", type=str, nargs="?", default=None)
parser.add_argument("ss", type=str, nargs="?", default=None)
parser.add_argument("ss2", type=str, nargs="?", default=None)

args = parser.parse_args()


class clause:
    def __init__(self, d: set["dis"], parent1: "clause" = None, parent2: "clause" = None, id : int = None, action:str = None):
        self.set = d
        self.parent1 = parent1
        self.parent2 = parent2
        self.id = id

    def __eq__(self, other):
        return isinstance(other, clause) and self.set == other.set

class dis:
    def __init__(self, neg: bool, name: str):
        self.neg = neg
        self.name = name
    def __hash__(self):
        return hash((self.name, self.neg))
    def __eq__(self, other):
        return isinstance(other, dis) and self.name == other.name and self.neg == other.neg
    def __str__(self):
        return f"{self.name} : {self.neg}"

def isTautology(c: set[dis]):
    for d in c:
        if dis(not d.neg, d.name) in c:
            return True
    return False

def resolve(a: clause, b: clause):
    resolvents = []
    for disA in a.set:
        for disB in b.set:
            if disA.name == disB.name and disA.neg != disB.neg:
                new_set = set()
                for el in a.set:
                    if el != disA:
                        new_set.add(el)
                for el in b.set:
                    if el != disB:
                        new_set.add(el)
                
                if not isTautology(new_set):
                    resolvents.append(clause(new_set, a, b))
                    
    return resolvents

def CanBeResolved(a: clause, b: clause):
    for disA in a.set:
        for disB in b.set:
            if disA.name == disB.name and disA.neg != disB.neg:
                return True
    return False

stringList = []

def printSolution(a:clause):
    if a is None:
        return
    string = ""
    for d in a.set:
        if d.neg:
            string += f"~{d.name} v "
        else:
            string += f"{d.name} v "
    string = string[:-2]
    if a.parent1 != None:
        string += f" ({a.parent1.id}, {a.parent2.id})"
    string = f"{a.id}. " + string
    stringList.append(string)
    printSolution(a.parent1)
    printSolution(a.parent2)

clauses = []

with open(args.ss, "r") as f:
    c = 0
    for line in f:
        if line.startswith("#"):
            continue
        clauseSet = set()
        for el in line.strip().lower().split(" v "):
            el = el.strip()
            if el.endswith("\n"):
                el = el[:-1]
            if el.startswith("~"):
                newDis = dis(True, el[1:])
            else:
                newDis = dis(False, el)
            clauseSet.add(newDis)
        newClause = clause(clauseSet)
        c += 1
        newClause.id = c
        clauses.append(newClause)

def startResolution():
    counter = 1
    finalClause = clauses.pop()

    for c in clauses:
        c.id = counter
        counter +=1

    SoS2 = []
    for el in finalClause.set:
        if el.neg:
            el.neg = False
        else:
            el.neg = True
        clauseSet = set()
        clauseSet.add(el)
        newClause = clause(clauseSet)
        newClause.id = counter
        counter += 1
        SoS2.append(newClause)
    
    while(True):
        newSos = []
        for first in SoS2:
            for second in SoS2:
                for r_clause in resolve(first, second):
                    if r_clause not in SoS2 and r_clause not in clauses and r_clause not in newSos:
                        r_clause.id = counter
                        counter+=1
                        newSos.append(r_clause)
            for second in clauses:
                for r_clause in resolve(first, second):
                    if r_clause not in SoS2 and r_clause not in clauses and r_clause not in newSos:
                        r_clause.id = counter
                        counter+=1
                        newSos.append(r_clause)

        for found in newSos:
            if len(found.set) == 0:
                finalString = f"{counter}. NIL ({found.parent1.id}, {found.parent2.id})"
                stringList.clear()
                printSolution(found.parent1)
                printSolution(found.parent2)
                string = ""
                for d in finalClause.set:
                    if d.neg:
                        string += f"{d.name} v "
                    else:
                        string += f"~{d.name} v "
                string = string[:-2]
                unique = list(dict.fromkeys(stringList))
                unique.sort(key=lambda s: float(s.split(". ")[0]))
                flag=True
                for el in unique:
                    if flag and "(" in el:
                        flag = False
                        print("=============")
                    print(el)
                print(finalString)
                print("================")
                print(f"[CONCLUSION]: {string} is true")
                clauses.append(finalClause)
                return

        filteredSos = []
        for a in newSos:
            found = False
            for b in SoS2 + clauses + newSos:
                if a is not b and b.set.issubset(a.set):
                    found = True
                    break
            if not found:
                filteredSos.append(a)

        added = False
        for newClause in filteredSos:
            if newClause not in SoS2 and newClause not in clauses:
                SoS2.append(newClause)
                added = True
                
        if (added==False):
            string = ""
            for d in finalClause.set:
                if d.neg:
                    string += f"{d.name} v "
                else:
                    string += f"~{d.name} v "
            string = string[:-2]
            print(f"[CONCLUSION]: {string} is unknown")
            clauses.append(finalClause)
            return


if args.alg == "resolution":
    startResolution()

if args.alg == "cooking":
    instructions = []
    with open(args.ss2, "r") as f:
        for line in f:
            action = line[-2]
            line = line[:-2]
            clauseSet = set()
            for el in line.strip().lower().split(" v "):
                el = el.strip()
                if el.endswith("\n"):
                    el = el[:-1]
                if el.startswith("~"):
                    newDis = dis(True, el[1:])
                else:
                    newDis = dis(False, el)
                clauseSet.add(newDis)
            newClause = clause(clauseSet)
            c += 1
            newClause.id = c
            
            newClause.action = action
            instructions.append(newClause)
    
    print("Constructed with knowledge:")
    for el in clauses:
        string = ""
        for d in el.set:
            if d.neg:
                string += f"~{d.name} v "
            else:
                string += f"{d.name} v "
        print(string[:-2])
    print()

    for instruction in instructions:
        string = ""
        for d in instruction.set:
            if d.neg:
                string += f"~{d.name} v "
            else:
                string += f"{d.name} v "
        string = string[:-2]
        if instruction.action == "?":
            print(f"User’s command: {string} ?")
            clauses.append(instruction)
            startResolution()
            print()
        elif instruction.action == "+":
            print(f"User’s command: {string} +")
            print(f"Added {string}")
            clauses.append(instruction)
            print()
        elif instruction.action == "-":
            print(f"User’s command: {string} -")
            print(f"removed {string}")
            clauses.remove(instruction)
            print()

