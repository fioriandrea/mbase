#! /usr/bin/python

import sys
from collections import deque
from enum import Enum

def mbase(matrix):
    maxM = eps_max - 1
    Q = deque()
    Q.append([0] * len(matrix[0]))
    while len(Q) > 0:
        father = Q.popleft()
        for e in range(succ(set_max(father)), eps_max):
            child = [x for x in father]
            child[e] = 1
            result = check(matrix, child)
            if result == Result.OK and e != maxM:
                Q.append(child)
            elif result == Result.MHS:
                output(child)

def check(matrix, bset):
    vector = []
    for row in matrix:
        count = 0
        common_element = None
        for j, (row_elem, ins_elem) in enumerate(zip(row, bset)):
            if ins_elem != 0 and ins_elem == row_elem:
                count = count + 1
                common_element = j
        if count == 1:
            vector.append(common_element)
        elif count == 0:
            vector.append('Z')
        else:
            vector.append('X')

    for i, elem in enumerate(bset):
        if elem == 1 and i not in vector:
            return Result.KO
    if 'Z' in vector:
        return Result.OK
    else:
        return Result.MHS
    
class Result(Enum):
    OK = 1
    KO = 2
    MHS = 3

def set_max(bset):
    result = eps_min
    for i in range(len(bset)):
        if bset[i] == 1:
            result = i
    return result

def set_min(bset):
    result = eps_min
    for i in range(len(bset) - 1, -1, -1):
        if bset[i] == 1:
            result = i
    return result

def succ(n):
    return n + 1

def pred(n):
    return n - 1

def cardinality(bset):
    return sum(bset)

def output(bset):
    global count
    global max_cardinality
    global min_cardinality
    count = count + 1
    min_cardinality = max(min_cardinality, cardinality(bset))
    max_cardinality = min(max_cardinality, cardinality(bset))

def show_results():
    print("MHS totali: %d\nCARDINALITA' MINIMA: %d\nCARDINALITA' MASSIMA: %s" % (count, max_cardinality, min_cardinality))

# preprocessing

def parse_matrix_file(filename):
    matrix = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith(';;;') or len(line.strip()) == 0:
                continue
            row = line.strip().split(' ')[:-1]
            row = [int(x) for x in row]
            matrix.append(row)
    return matrix

def remove_rows(matrix):
    newmatrix = []
    for row in matrix:
        toremove = False
        for other in matrix:
            if other == row:
                continue
            if is_subset(row, other):
                toremove = True
                break
        if not toremove:
            newmatrix.append(row)
    return newmatrix

def is_subset(subset, superset):
    result = True
    for sub_element, super_element in zip(subset, superset):
        if sub_element == 1 and super_element != 1:
            result = False
            break
    return result

def remove_columns(matrix):
    toremove = set()
    for c in range(len(matrix[0])):
        all_zeros = True
        for r in range(len(matrix)):
            if matrix[r][c] != 0:
                all_zeros = False
                break
        if all_zeros:
            toremove.add(c)

    toreturn = []
    for row in matrix:
        newrow = []
        for c in range(len(row)):
            if c not in toremove:
                newrow.append(row[c])
        if len(newrow) != 0:
            toreturn.append(newrow)
    return toreturn

progname = sys.argv[0]        
args = sys.argv[1:]

if len(args) == 0:
    print("usage: %s FILE..." % (progname), file=sys.stderr)
    sys.exit(1)

eps_min = -1
eps_max = None
count = 0
max_cardinality = None
min_cardinality = 0
optimize = False

for arg in args:
    matrix = parse_matrix_file(arg)
    if len(matrix) == 0:
        continue
    if optimize:
        matrix = remove_rows(matrix)
        matrix = remove_columns(matrix)
    eps_max = len(matrix[0])
    max_cardinality = len(matrix[0])
    try:
        mbase(matrix)
    except KeyboardInterrupt:
        pass
    show_results()