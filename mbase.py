#! /usr/bin/python

import sys
from collections import deque
from enum import Enum
                
def from_matrix_to_set_list(matrix):
    set_list = []
    for row in matrix:
        current_set = set()
        for c in range(len(row)):
            if row[c] != 0:
                current_set.add(c)
        set_list.append(current_set)
    return set_list


def mbase(set_list):
    maxM = eps_max - 1
    Q = deque()
    Q.append(set())
    while len(Q) > 0:
        father = Q.popleft()
        for e in range(succ(set_max(father)), eps_max):
            child = father | set([e])
            result = check(set_list, child)
            if result == Result.OK and e != maxM:
                Q.append(child)
            elif result == Result.MHS:
                output(child)

def check(set_list, sigma):
    vector = set()
    for row in set_list:
        intersection = row & sigma
        if len(intersection) == 0:
            vector.add('Z')
        elif len(intersection) == 1:
            vector = vector | intersection
        else:
            vector.add('X')
    if len(vector & sigma) != len(sigma):
        return Result.KO
    elif 'Z' in vector:
        return Result.OK
    else:
        return Result.MHS

class Result(Enum):
    OK = 1
    KO = 2
    MHS = 3

def set_max(bset):
    result = eps_min
    for element in bset:
        result = max(element, result)
    return result

def succ(n):
    return n + 1

def cardinality(bset):
    return len(bset)

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
    set_list = from_matrix_to_set_list(matrix)
    try:
        mbase(set_list)
    except KeyboardInterrupt:
        pass
    show_results()