#! /usr/bin/python

import sys
from collections import deque
from enum import Enum

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

def togli_righe(matrix):
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

def togli_colonne(matrix):
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

def max_insieme(insieme):
    result = eps_min
    for i in range(len(insieme)):
        if insieme[i] == 1:
            result = i
    return result

def min_insieme(insieme):
    result = eps_min
    for i in range(len(insieme) - 1, -1, -1):
        if insieme[i] == 1:
            result = i
    return result

def succ(n):
    return n + 1

def pred(n):
    return n - 1

def cardinalita(insieme):
    return sum(insieme)

class Result(Enum):
    OK = 1
    KO = 2
    MHS = 3

def check(matrix, insieme):
    vettore = []
    for row in matrix:
        count = 0
        unique_element_common = None
        for j, (row_elem, ins_elem) in enumerate(zip(row, insieme)):
            if ins_elem != 0 and ins_elem == row_elem:
                count = count + 1
                unique_element_common = j
        if count == 1:
            vettore.append(unique_element_common)
        elif count == 0:
            vettore.append('Z')
        else:
            vettore.append('X')

    for i, elem in enumerate(insieme):
        if elem == 1 and i not in vettore:
            return Result.KO
    if 'Z' in vettore:
        return Result.OK
    else:
        return Result.MHS

    
def output(insieme):
    global count
    global cardinalita_min
    global cardinalita_max
    count = count + 1
    cardinalita_max = max(cardinalita_max, cardinalita(insieme))
    cardinalita_min = min(cardinalita_min, cardinalita(insieme))

def mostra_risultati():
    print("MHS totali: %d\nCARDINALITA' MINIMA: %d\n CARDINALITA' MASSIMA: %s" % (count, cardinalita_min, cardinalita_max))

def mbase(matrix):
    maxM = eps_max - 1
    Q = deque()
    Q.append([0] * len(matrix[0]))
    while len(Q) > 0:
        father = Q.popleft()
        for e in range(succ(max_insieme(father)), eps_max):
            child = [x for x in father]
            child[e] = 1
            result = check(matrix, child)
            if result == Result.OK and e != maxM:
                Q.append(child)
            elif result == Result.MHS:
                output(child)

progname = sys.argv[0]        
args = sys.argv[1:]

if len(args) == 0:
    print("usage: %s FILE..." % (progname), file=sys.stderr)
    sys.exit(1)

eps_min = -1
eps_max = None
count = 0
cardinalita_min = None
cardinalita_max = 0
ottimizza = True

for arg in args:
    matrix = parse_matrix_file(arg)
    if len(matrix) == 0:
        continue
    if ottimizza:
        matrix = togli_righe(matrix)
        matrix = togli_colonne(matrix)
    eps_max = len(matrix[0])
    cardinalita_min = len(matrix[0])
    try:
        mbase(matrix)
    except KeyboardInterrupt:
        pass
    mostra_risultati()