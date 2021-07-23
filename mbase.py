#! /usr/bin/python

import sys
from collections import deque
import signal
import os.path
import time

# algorithm

def mbase(set_list, eps_max):
    maxM = eps_max - 1
    Q = deque()
    Q.append(set())
    while len(Q) > 0:
        father = Q.popleft()
        for e in range(succ(set_max(father)), eps_max):
            child = father | set([e])
            result = check(child, set_list)
            if result == 'OK' and e != maxM:
                Q.append(child)
            elif result == 'MHS':
                output(child)

def check(sigma, set_list):
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
        return 'KO'
    elif 'Z' in vector:
        return 'OK'
    else:
        return 'MHS'

def set_max(s):
    if len(s) == 0:
        return -1
    return max(s)

def succ(n):
    return n + 1

def cardinality(s):
    return len(s)

def set_to_string(s):
    return str(s)

# file output

def output(s):
    global count
    global max_cardinality
    global min_cardinality
    global out_file
    global out_queue
    count = count + 1
    min_cardinality = min(min_cardinality, cardinality(s))
    max_cardinality = max(max_cardinality, cardinality(s))
    out_queue.append(s)
    if len(out_queue) > 100000:
        dump_out_queue(out_queue, out_file)

def write_header(out_file, matrix, matrix_name, optimize):
    print('Matrice: %s' % (matrix_name), file=out_file)
    print('Numero insiemi: %s' % (len(matrix)), file=out_file)
    print('Numero elementi dominio: %s' % (len(matrix[0])), file=out_file)
    print('', file=out_file)
    print('Inizio elaborazione (%s)' % ('con preprocessing' if optimize else 'senza preprocessing'), file=out_file)
    print('', file=out_file)

def write_trailer(out_file, count, min_cardinality, max_cardinality, execution_time):
    print('', file=out_file)
    print('Numero hitting set trovati: %d' % (count), file=out_file)
    print('Cardinalità minima: %d' % (min_cardinality), file=out_file)
    print('Cardinalità massima: %d' % (max_cardinality), file=out_file)
    print('Tempo di esecuzione: %f secondi' % (execution_time), file=out_file)
    print('--------------------------------', file=out_file)

def dump_out_queue(out_queue, out_file):
    while len(out_queue) > 0:
        print(set_to_string(out_queue.popleft()), file=out_file)

# preprocessing

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

# input parsing
 
def from_matrix_to_set_list(matrix):
    set_list = []
    for row in matrix:
        current_set = set()
        for c in range(len(row)):
            if row[c] != 0:
                current_set.add(c)
        set_list.append(current_set)
    return set_list

def parse_matrix_file(filename):
    matrix = []
    with open(filename, 'r') as out_file:
        for line in out_file:
            if line.startswith(';;;') or len(line.strip()) == 0:
                continue
            row = line.strip().split(' ')[:-1]
            row = [int(x) for x in row]
            matrix.append(row)
    return matrix


# main

progname = sys.argv[0]        
args = sys.argv[1:]

if len(args) == 0:
    print("usage: %s FILE..." % (progname), file=sys.stderr)
    sys.exit(1)

eps_max = None
count = None
max_cardinality = None
min_cardinality = None
matrix_name = None
matrix = None
out_queue = None

for arg in args:
    matrix = parse_matrix_file(arg)
    matrix_name = os.path.basename(arg)
    out_queue = deque()
    with open(matrix_name + '.output', 'w') as out_file:
        for optimize in (False, True):
            start_time = time.time()
            if len(matrix) == 0:
                continue
            if optimize:
                matrix = remove_rows(matrix)
                matrix = remove_columns(matrix)
            count = 0
            eps_max = len(matrix[0])
            min_cardinality = len(matrix[0])
            max_cardinality = 0
            set_list = from_matrix_to_set_list(matrix)
            try:
                print('Inizio elaborazione (%s)' % ('con preprocessing' if optimize else 'senza preprocessing'))
                write_header(out_file, matrix, matrix_name, optimize)
                mbase(set_list, eps_max)
            except KeyboardInterrupt:
                print('Esecuzione interrotta')
                sys.exit(0)
            finally:
                dump_out_queue(out_queue, out_file)
                print('Fine elaborazione (%s)' % ('con preprocessing' if optimize else 'senza preprocessing'))
                execution_time = time.time() - start_time
                write_trailer(out_file, count, min_cardinality, max_cardinality, execution_time)