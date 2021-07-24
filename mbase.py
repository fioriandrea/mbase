#! /usr/bin/python

from collections import deque
import os.path
import pathlib
import sys
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

# file output

def output(s):
    global count
    global max_cardinality
    global min_cardinality
    global out_file
    global out_queue
    global out_queue_threshold
    count = count + 1
    min_cardinality = min(min_cardinality, len(s))
    max_cardinality = max(max_cardinality, len(s))
    out_queue.append(s)
    if len(out_queue) > out_queue_threshold:
        dump_out_queue(out_queue, out_file)

def write_prelude(out_file):
    global matrix_name
    global domain_symbols
    global matrix
    print('Matrice: %s' % (matrix_name), file=out_file)
    print('Dominio: %s' % (str(domain_symbols)), file=out_file)
    print('Numero di insiemi: %d' % (len(matrix)), file=out_file)
    print('Numero di elementi nel dominio: %d' % (len(domain_symbols)), file=out_file)
    print('', file=out_file)

def write_header(out_file):
    global n_rows
    global n_columns
    global matrix_name
    global optimize
    global removed_columns
    global removed_rows
    print('Elaborazione %s' % ('con preprocessing' if optimize else 'senza preprocessing'), file=out_file)
    print('Matrice: %s' % (matrix_name), file=out_file)
    print('Numero insiemi: %s' % (n_rows), file=out_file)
    print('Numero elementi dominio: %d' % (n_columns + len(removed_columns)), file=out_file)
    if optimize:
        print('Numero righe rimosse: %d' % len(removed_rows), file=out_file)
        print('Numero colonne rimosse: %d' % len(removed_columns), file=out_file)
    print('', file=out_file)

def write_trailer(out_file):
    global count
    global min_cardinality
    global max_cardinality
    global execution_time
    global prev_execution_time
    global optimize
    global interrupted
    print('', file=out_file)
    if interrupted:
        print('Esecuzione interrotta prematuramente\n', file=out_file)
    print('Numero hitting set trovati: %d' % (count), file=out_file)
    if min_cardinality <= max_cardinality:
        print('Cardinalità minima: %d' % (min_cardinality), file=out_file)
        print('Cardinalità massima: %d' % (max_cardinality), file=out_file)
    print('Tempo di esecuzione: %f secondi' % (execution_time), file=out_file)
    print('--------------------------------', file=out_file)

def write_epilogue(out_file):
    global prev_execution_time
    global execution_time
    global removed_columns
    global removed_rows
    print('', file=out_file)
    print('Resoconto finale', file=out_file)
    print('Guadagno in tempo di esecuzione dopo il preprocessing: %f secondi' % (prev_execution_time - execution_time), file=out_file)
    print('Insieme degli indici di righe rimosse: %s' % (set_to_string_given_symbols(removed_rows, {i: str(i + 1) for i in removed_rows})), file=out_file)
    print('Insieme delle colonne rimosse: %s' % (set_to_string_given_symbols(removed_columns, domain_symbols)), file=out_file)

def set_to_string_given_symbols(s, symbols):
    buffer = []
    for elem in s:
        symbol = symbols[elem]
        buffer.append(symbol)
    return '{' + ','.join(buffer) + '}'

def dump_out_queue(out_queue, out_file):
    while len(out_queue) > 0:
        print(set_to_string(out_queue.popleft()), file=out_file)

def set_to_string(s):
    global output_format
    return output_format(s)

def set_to_string_matrix(s):
    global n_columns
    global removed_columns
    global output_columns
    s = {output_columns[elem] for elem in s}
    buffer = ['0'] * (n_columns + len(removed_columns)) 
    for i in s:
        buffer[i] = '1'
    return ' '.join(buffer) + ' -'  

def set_to_string_symbols(s):
    global domain_symbols
    global output_columns
    buffer = []
    for elem in s:
        index = output_columns[elem]
        symbol = domain_symbols[index]
        buffer.append(symbol)
    return '{' + ','.join(buffer) + '}'

# preprocessing

def rows_to_remove(matrix):
    result = set()
    for i, row in enumerate(matrix):
        toremove = False
        for other in matrix:
            if other == row:
                continue
            if is_subset(row, other):
                toremove = True
                break
        if toremove:
            result.add(i)
    return result

def is_subset(subset, superset):
    result = True
    for sub_element, super_element in zip(subset, superset):
        if sub_element == 1 and super_element != 1:
            result = False
            break
    return result

def remove_rows(matrix, toremove):
    return [matrix[i] for i in range(len(matrix)) if i not in toremove]

def columns_to_remove(matrix):
    toremove = set()
    for c in range(len(matrix[0])):
        all_zeros = True
        for r in range(len(matrix)):
            if matrix[r][c] != 0:
                all_zeros = False
                break
        if all_zeros:
            toremove.add(c)
    return toremove

def remove_columns(matrix, toremove):
    toreturn = []
    for row in matrix:
        newrow = []
        for c in range(len(row)):
            if c not in toremove:
                newrow.append(row[c])
        if len(newrow) != 0:
            toreturn.append(newrow)
    return toreturn

def compute_output_columns(removed_columns, n_columns):
    count_before = 0
    result = [0] * (n_columns - len(removed_columns))
    for i in range(n_columns - len(removed_columns)):
        while i + count_before in removed_columns:
            count_before += 1
        result[i] = i + count_before
    return result

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
    global domain_symbols
    global matrix
    matrix = []
    with open(filename, 'r') as out_file:
        for line in out_file:
            if line.startswith(';;; Map'):
                line = line[len(';;; Map'):]
                domain_symbols = parse_mapping(line)
                continue
            if line.startswith(';;;') or len(line.strip()) == 0:
                continue
            row = line.strip().split(' ')[:-1]
            row = [int(x) for x in row]
            matrix.append(row)
    if domain_symbols == None:
        domain_symbols = [str(i + 1) for i in range(len(matrix[0]))]
    for i in range(len(matrix[0]) - len(domain_symbols)):
        domain_symbols.append('unlisted' + str(i + 1))
    return matrix

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

    domain_symbols = []
    while i < len(line):
        skip_spaces()
        skip_digits()
        i = i + 1 # salta parentesi (
        domain_symbols.append(read_symbol())
        i = i + 1 # salta parentesi )
        skip_spaces()
    return domain_symbols

# main

def print_usage(file=sys.stdout):
    global progname
    print("usage: %s [OPTIONS] FILE..." % (progname), file=file)

def parse_cli_args():
    global destination_directory
    global filenames
    global out_queue_threshold
    global output_format
    i = 1
    try:
        while i < len(sys.argv):
            if sys.argv[i] == '--dir':
                destination_directory = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--qthresh':
                out_queue_threshold = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == '--outmat':
                output_format = set_to_string_matrix
                i += 1
            elif sys.argv[i] == '--outsym':
                output_format = set_to_string_symbols
                i += 1
            elif sys.argv[i] in ('--help', '-h'):
                print_usage()
                sys.exit(0)
            else:
                filenames = sys.argv[i:]
                break
    except IndexError:
        print('expected argument for %s option' % (sys.argv[i]), file=sys.stderr)
        print_usage(file=sys.stderr)
        sys.exit(1)

progname = sys.argv[0]
eps_max = None
count = None
max_cardinality = None
min_cardinality = None
n_rows = None
n_columns = None
matrix_name = None
matrix = None
out_file = None
out_queue = None
optimize = None
removed_columns = None
removed_rows = None
domain_symbols = None
output_columns = None
execution_time = None
prev_execution_time = None
output_format = set_to_string_symbols
out_queue_threshold = 100000
destination_directory = '.'
interrupted = False
filenames = []

parse_cli_args()

if len(filenames) == 0:
    print("usage: %s [OPTIONS] FILE..." % (progname), file=sys.stderr)
    sys.exit(1)

pathlib.Path(destination_directory).mkdir(parents=True, exist_ok=True) 

for filename in filenames:
    matrix = parse_matrix_file(filename)
    matrix_name = os.path.basename(filename)
    out_queue = deque()
    with open(destination_directory + '/' + matrix_name + '.output', 'w') as out_file:
        write_prelude(out_file)
        for optimize in (False, True):
            removed_columns = set()
            removed_rows = set()
            if optimize:
                removed_rows = rows_to_remove(matrix)
                matrix = remove_rows(matrix, removed_rows)
                removed_columns = columns_to_remove(matrix)
                matrix = remove_columns(matrix, removed_columns)
            count = 0
            n_rows = len(matrix)
            n_columns = len(matrix[0])
            output_columns = compute_output_columns(removed_columns, n_columns + len(removed_columns))
            eps_max = n_columns
            min_cardinality = n_columns
            max_cardinality = 0
            set_list = from_matrix_to_set_list(matrix)
            start_time = time.time()
            try:
                print('Inizio elaborazione %s (%s)' % (matrix_name, 'con preprocessing' if optimize else 'senza preprocessing'))
                write_header(out_file)
                mbase(set_list, eps_max)
            except KeyboardInterrupt:
                print('Esecuzione interrotta')
                interrupted = True
                sys.exit(0)
            finally:
                dump_out_queue(out_queue, out_file)
                print('Fine elaborazione %s (%s)' % (matrix_name, 'con preprocessing' if optimize else 'senza preprocessing'))
                prev_execution_time = execution_time
                execution_time = time.time() - start_time
                write_trailer(out_file)
        write_epilogue(out_file)
