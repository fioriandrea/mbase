#! /usr/bin/python

import sys
from collections import deque
from multiprocessing import Process, Queue
import signal
import os.path
 
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
            if result == 'OK' and e != maxM:
                Q.append(child)
            elif result == 'MHS':
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
        return 'KO'
    elif 'Z' in vector:
        return 'OK'
    else:
        return 'MHS'

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
    global pqueue
    global count
    global max_cardinality
    global min_cardinality
    count = count + 1
    min_cardinality = min(min_cardinality, cardinality(bset))
    max_cardinality = max(max_cardinality, cardinality(bset))
    pqueue.put(bset)

def set_to_string(s):
    global symbol_mapping
    if symbol_mapping == None:
        return str(s)
    buffer = []
    for elem in s:
        buffer.append(symbol_mapping[elem])
    return '{' + ','.join(buffer) + '}'

def file_writer(pqueue, matrix_name, matrix, optimize):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    filename = matrix_name + '.output.txt'
    print(filename)
    with open(filename, 'w') as f:
        print('Matrice: %s' % (matrix_name), file=f)
        print('Numero insiemi: %s' % (len(matrix)), file=f)
        print('Numero elementi dominio: %s' % (len(matrix[0])), file=f)
        if optimize:
            print('Inizio elaborazione (con preprocessing)', file=f)
        else:
            print('Inizio elaborazione (senza preprocessing)', file=f)
        while True:
            s = pqueue.get()
            if s == 'COMPLETED':
                break
            print(set_to_string(s), file=f)
        count = pqueue.get()
        min_cardinality = pqueue.get()
        max_cardinality = pqueue.get()
        print('Numero hitting set trovati: %d' % (count), file=f)
        print('Cardinalità minima: %d' % (min_cardinality), file=f)
        print('Cardinalità massima: %d' % (max_cardinality), file=f)

# preprocessing

def parse_mapping(line):
    i = 0
    def skip_spaces():
        nonlocal line
        nonlocal i
        while i < len(line) and line[i] in (' ', '\n', '\t'):
            i = i + 1

    def skip_digits():
        nonlocal line
        nonlocal i
        while i < len(line) and line[i] >= '0' and line[i] <= '9':
            i = i + 1

    def read_symbol():
        nonlocal line
        nonlocal i
        buffer = []
        while i < len(line) and line[i] != ')':
            buffer.append(line[i])
            i = i + 1
        return ''.join(buffer)

    global symbol_mapping
    symbol_mapping = []
    while i < len(line):
        skip_spaces()
        skip_digits()
        i = i + 1 # salta parentesi (
        symbol_mapping.append(read_symbol())
        i = i + 1 # salta parentesi )
        skip_spaces()
    return symbol_mapping

def parse_matrix_file(filename):
    matrix = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith(';;; Map'):
                line = line[len(';;; Map'):]
                parse_mapping(line)
                continue
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
min_cardinality = None
optimize = False
symbol_mapping = None
matrix = None
pqueue = None

for arg in args:
    matrix = parse_matrix_file(arg)
    if len(matrix) == 0:
        continue
    if optimize:
        matrix = remove_rows(matrix)
        matrix = remove_columns(matrix)
    eps_max = len(matrix[0])
    min_cardinality = len(matrix[0])
    max_cardinality = 0
    set_list = from_matrix_to_set_list(matrix)
    pqueue = Queue()
    matrix_name = os.path.basename(arg)
    writer = Process(target=file_writer, args=(pqueue, matrix_name, matrix, optimize))
    writer.start()
    try:
        mbase(set_list)
    except KeyboardInterrupt:
        pass
    pqueue.put('COMPLETED')
    pqueue.put(count)
    pqueue.put(min_cardinality)
    pqueue.put(max_cardinality)