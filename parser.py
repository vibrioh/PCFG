#! /usr/bin/python

__author__ = "Jun Hu <jh3846@columbia.edu>"
__data__ = "$Oct 26, 2017"

import os
import sys
import json
from collections import defaultdict

'''
count the frequencies as count_cfg_freq.py does
'''


class Counts:
    def __init__(self):
        # focusing on count terminals/leaves only
        self.cnt_trmnls = defaultdict(int)

    def count(self, tree):
        # when tree branches come to some leaves, which are instances of string/unicode
        if isinstance(tree, basestring):
            return

        # when {X -> [Y, Z]}, recursively call count()
        if len(tree) == 3:
            self.count(tree[1])
            self.count(tree[2])
        # when {X -> t}, count the terminal words
        elif len(tree) == 2:
            self.cnt_trmnls[tree[1]] += 1


'''
replace words < 5 with _RARE_
'''


def replace(tree):
    if isinstance(tree, basestring):
        return
    # when {X -> [Y, Z]}, recursively call replace()
    if len(tree) == 3:
        replace(tree[1])
        replace(tree[2])
    # when {X -> t}, check rare and replace
    if len(tree) == 2:
        # replace with less than 5 counts
        if counter.cnt_trmnls[tree[1]] < 5:
            tree[1] = "_RARE_"


'''
use cfg.counts to parse input sentences
'''


class Parse:
    # set all params for the PCGF
    def __init__(self):
        self.N = defaultdict(int)
        self.epsilon = set()
        self.qUR = defaultdict(float)
        self.X_YZ = defaultdict(set)
        self.qBR = defaultdict(float)
        self.pi = defaultdict(float)
        self.bp = defaultdict(tuple)

    # compute q for all rules and record terminal words
    # record all legal rules
    def compute_params(self, count_file):
        with open(count_file, "r") as file:
            for line in file:
                ls = line.strip().split(' ')
                if ls[1] == "NONTERMINAL":
                    self.N[ls[2]] = ls[0]
            file.seek(0)
            for line in file:
                ls = line.strip().split(' ')
                if ls[1] == "UNARYRULE":
                    self.qUR[(ls[2], ls[3])] = float(ls[0]) / float(self.N[ls[2]])
                    self.epsilon.add(ls[3])
                if ls[1] == "BINARYRULE":
                    self.qBR[(ls[2], ls[3], ls[4])] = float(ls[0]) / float(self.N[ls[2]])
                    self.X_YZ[ls[2]].add((ls[3], ls[4]))

    def cky(self, sentence):
        # make sentence to words list
        # keep original words list
        # rare replace the words
        origin_words = sentence.strip().split(" ")
        words = sentence.strip().split(" ")
        n = len(words)
        self.replace_RARE(words, n)

        # Initialization pi(i, i, X)
        for i in xrange(1, n + 1):
            for X in self.N:
                # if (X, words[i - 1]) in self.qUR.keys():
                self.pi[(i, i, X)] = self.qUR[(X, words[i - 1])]

        # CKY main algorithm
        for l in xrange(1, n):
            for i in xrange(1, n - l + 1):
                j = i + l
                # use only legal rules
                for X in self.X_YZ:
                    pi_max = float("-Inf")
                    for (Y, Z) in self.X_YZ[X]:
                        for s in xrange(i, j):
                            # filter for the rules
                            if (i, s, Y) not in self.pi or (s + 1, j, Z) not in self.pi:
                                continue
                            curr = self.qBR[(X, Y, Z)] * self.pi[(i, s, Y)] * self.pi[(s + 1, j, Z)]
                            if pi_max < curr:
                                pi_max = curr
                                self.pi[(i, j, X)] = pi_max
                                self.bp[(i, j, X)] = (Y, Z, s)

        # pi[1, n, S] == 0, which is not in bp, return pi[1, n, X]
        S = "S"
        if self.pi[(1, n, S)] == 0:
            for X in self.X_YZ:
                if self.pi[(1, n, X)] > self.pi[(1, n, S)]:
                    S = X
        # rebuild trees with original sentences words and output as json format
        return json.dumps(self.point_back(origin_words, 1, n, S))

    # recursively backtrack the stored symbols
    def point_back(self, words, i, j, X):
        tree = [X]
        if i == j:
            tree.append(words[i - 1])
        else:
            Y, Z, s = self.bp[(i, j, X)]
            tree.append(self.point_back(words, i, s, Y))
            tree.append(self.point_back(words, s + 1, j, Z))
        return tree

    # replace test corpus words with _RARE_
    def replace_RARE(self, words, n):
        for i in xrange(n):
            if words[i] not in self.epsilon:
                words[i] = "_RARE_"


if __name__ == '__main__':
    # this part solves problem 4, regarding "q4" argument
    if sys.argv[1] == "q4":
        # print sys.argv[1]
        counter = Counts()
        # read original parse_train.dat
        with open(sys.argv[2], 'r') as f:
            for l in f:
                tree = json.loads(l)
                counter.count(tree)
        # replace the rare terminal words and output parse_train.RARE.dat
        with open(sys.argv[2], 'r') as f:
            with open(sys.argv[3], 'w') as output:
                for l in f:
                    tree = json.loads(l)
                    replace(tree)
                    l = json.dumps(tree)
                    output.write(l + "\n")

    # this part solves problem 5 and problem 6, regrading "q5" or "q6" argument
    if sys.argv[1] == "q5" or sys.argv[1] == "q6":
        # print sys.argv[1]
        # generate cfg.counts for the parsing process
        os.system("python count_cfg_freq.py " + sys.argv[2] + " > cfg.counts")
        # use cfg.counts to compute q params
        with open(sys.argv[4], 'w') as output:
            parser = Parse()
            parser.compute_params("cfg.counts")
            with open(sys.argv[3], 'r') as f:
                for l in f:
                    output.write(parser.cky(l) + "\n")
