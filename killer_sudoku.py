import numpy as np
import math
import pycosat
import itertools
import csv

def sum_permutations(sum_total, num_amount_needed):
    nums = np.array([1,2,3,4,5,6,7,8,9])
    all_perms = list(itertools.combinations(nums, num_amount_needed))
    sum_perms = [p for p in all_perms if sum(p) == sum_total]
    return sum_perms

def load_rules(filename):
    rules = []
    
    with open("C:\\Users\\Gebruiker\\Documents\\easy_sudoku_rules.txt") as f:
        reader = csv.reader(f, delimiter=',')
        
        for line in reader:
            sum_list = [int(i) for i in line]
            num_amount_needed = len(sum_list)-1
            perms = sum_permutations(sum_list[-1], num_amount_needed)
    
            for i in range(len(sum_list)-1):
                node_rule = []
                for j in range(0, len(perms)):
                    rule = int(str(sum_list[i]) + str(perms[j][i]))
                    node_rule.append(rule)
                rules.append(node_rule)
    return rules

sudokumatrix = np.loadtxt("C:\\Users\\Gebruiker\\Documents\\easy_killer_sudoku.txt", dtype=int, delimiter=',')
rules = load_rules("C:\\Users\\Gebruiker\\Documents\\easy_sudoku_rules.txt")
print(rules)

#wondering if it's necessary to add all neg rules too?