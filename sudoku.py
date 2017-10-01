from pprint import pprint
import numpy as np
import pycosat
import itertools
import csv


def sum_permutations(summers_needed, sum_total):
    nums = np.array([1,2,3,4,5,6,7,8,9])
    all_perms = list(itertools.combinations(nums, summers_needed))
    sum_perms = [p for p in all_perms if sum(p) == sum_total]
    return sum_perms

def load_sum_rules(blocks):
    rules = []

    for _, (summers, sum_total) in blocks.items():
        summers_needed = len(summers)
        perms = sum_permutations(len(summers), sum_total)

        for i in range(summers_needed):
            node_rule = []

            for j in range(0, len(perms)):
                currentPerm = perms[j]
                for k in currentPerm:
                    rule = str(summers[i]) + str(k)
                    node_rule.append(rule)
            rules.append(node_rule)

    return rules

def load_blocks(filename, indices):
    blocks = {}
    with open(filename) as f:
        reader = csv.reader(f, delimiter=',')

        count = 0
        for line in reader:
            sum_list = [int(i) for i in line]
            block_sum = sum_list[-1]
            summers = sum_list[0:-1]
            for summer in summers:
                blocks[summer] = (summers, block_sum)

    return blocks

#convert rules to correct cnf
def convert_rules(rules):
    res = []
    for rule in rules:
        single_clause = []
        for clause in range(0, len(rule)):
            if len(rule[clause]) > 2:
                if rule[clause][0] != '-':
                    single_clause.append(v(int(str(rule[clause])[:-1]) // 9 + 1, int(str(rule[clause])[:-1]) % 9 + 1,
                        int(str(rule[clause])[len(str(rule[clause])) - 1])))
                else:
                    single_clause.append(-v(int(str(rule[clause])[1:-1]) // 9 + 1, int(str(rule[clause])[1:-1]) % 9 + 1,
                                           int(str(rule[clause])[len(str(rule[clause])) - 1])))
            else:
                single_clause.append(v(int(rule[clause][0]) // 9 + 1, int(rule[clause][0]) % 9 + 1, int(rule[clause][1])))
        res.append(single_clause)
    return res

#zet de sudoku om naar de juiste vorm
def sudoku_form2(x):
    empty_sudoku = [[0] * 9 for j in range(9)]
    for i in range(0, 81):
        empty_sudoku[int(i / 9)][i % 9] = x[int(i / 9)][i % 9]
    return empty_sudoku

# deze functie lijkt door de komst van versie 2 overbodig, afhankelijk van de inputvorm van de sudoku
def sudoku_form(x):
    test_sudoku = [[0]* 9 for j in range(9)]
    for i in range(0, 81):
        test_sudoku[int(i / 9)][i % 9] = int(x[i])
    return  test_sudoku

def load_implication_rules(blocks, indices):
    implication_rules = []

    for i in range(indices):
        (summers, sum_total) = blocks[i]
        if (len(summers) == 1):
            continue
        perms = sum_permutations(len(summers), sum_total)
        perm_list = []
        for perm in perms:
            for value in perm:
                if (not value in perm_list):
                    perm_list.append(value)

        elements = []
        for value in perm_list:
            element = str(i) + str(value)
            elements.append(element)

        for element in elements:
            implied_elements = list(elements)
            implied_elements.remove(element)

            rule = ["-" + element]
            for implied_element in implied_elements:
                rule_copy = list(rule)
                rule_copy.append("-" + implied_element)
                implication_rules.append(rule_copy)

        rule = []
        for value in perm_list:
            rule.append("-" + str(i) + str(value))
            summers_copy = list(summers)
            summers_copy.remove(i)
            for summer in summers_copy:
                rule.append("-" + str(summer) + str(value))
            implication_rules.append(rule)
            rule = []

    return implication_rules

def v(i, j, d):
    """
    Return the number of the variable of cell i, j and digit d,
    which is an integer in the range of 1 to 729 (including).
    """
    return 81 * (i - 1) + 9 * (j - 1) + d

def standard_sudoku_clauses():
    """
    Create the (11745) Sudoku clauses, and return them as a list.
    Note that these clauses are *independent* of the particular
    Sudoku puzzle at hand.
    """
    res = []
    # for all cells, ensure that the each cell:
    for i in range(1, 10):
        for j in range(1, 10):
            # denotes (at least) one of the 9 digits (1 clause)
            res.append([v(i, j, d) for d in range(1, 10)])
            # does not denote two different digits at once (36 clauses)
            for d in range(1, 10):
                for dp in range(d + 1, 10):
                    res.append([-v(i, j, d), -v(i, j, dp)])


    def valid(cells):
        # Append 324 clauses, corresponding to 9 cells, to the result.
        # The 9 cells are represented by a list tuples.  The new clauses
        # ensure that the cells contain distinct values.
        for i, xi in enumerate(cells):
            for j, xj in enumerate(cells):
                if i < j:
                    for d in range(1, 10):
                        res.append([-v(xi[0], xi[1], d), -v(xj[0], xj[1], d)])

    # ensure rows and columns have distinct values
    for i in range(1, 10):
        valid([(i, j) for j in range(1, 10)])
        valid([(j, i) for j in range(1, 10)])
    # ensure 3x3 sub-grids "regions" have distinct values
    for i in 1, 4, 7:
        for j in 1, 4 ,7:
            valid([(i + k % 3, j + k // 3) for k in range(9)])

    assert len(res) == 81 * (1 + 36) + 27 * 324
    return res

def solve(grid):
    """
    solve a Sudoku grid inplace
    """
    clauses = standard_sudoku_clauses()
    for i in range(1, 10):
        for j in range(1, 10):
            d = grid[i - 1][j - 1]
            # For each digit already known, a clause (with one literal).
            # Note:
            #     We could also remove all variables for the known cells
            #     altogether (which would be more efficient).  However, for
            #     the sake of simplicity, we decided not to do that.
            if d:
                clauses.append([v(i, j, d)])

    # load all information about the new sudoku
    indices_amount = len(new_sudoku) * len(new_sudoku)
    blocks = load_blocks("./easy_sudoku_rules.txt", indices_amount)
    sum_rules = convert_rules(load_sum_rules(blocks))
    killer_sudoku_clauses = convert_rules(load_implication_rules(blocks, indices_amount))

    # add all clauses in correct form
    for i in range(0, len(killer_sudoku_clauses)):
        clauses.append(killer_sudoku_clauses[i])

    # add all clauses in correct form
    for i in range(0, len(sum_rules)):
        clauses.append(sum_rules[i])

    # solve the SAT problem
    sol = set(pycosat.solve(clauses))

    def read_cell(i, j):
        # return the digit of cell i, j according to the solution
        for d in range(1, 10):
            if v(i, j, d) in sol:
                return d

    for i in range(1, 10):
        for j in range(1, 10):
            grid[i - 1][j - 1] = read_cell(i, j)


#nieuwe lege sudoku
empty_sudoku = [[0] * 9 for j in range(9)]
new_sudoku = sudoku_form2(empty_sudoku)

solve(new_sudoku)
pprint(new_sudoku)
