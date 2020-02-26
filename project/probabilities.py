from __future__ import division
from nltk import bigrams
import numpy as np


def transmatrix(type_sequence):
    cat_number = 12  # edit if changed

    # type_vector_tuples
    tuples = list(bigrams(type_sequence))

    # make co-occurrence matrix of type bi-grams (for sentence bi-gram, many type bi-grams may be possible)
    # eg. sentence1 has t1 & t2, sentence 2 has t3. Then transitions (t1-t3), (t2-t3) are counted!
    matrix = np.zeros((cat_number, cat_number), int)
    for tup in tuples:
        combinations = [(type1, type2) for type1 in tup[0] for type2 in tup[1]]
        for (t1, t2) in combinations:
            matrix[t1][t2] += 1

    # for (markov) transition probability matrix, all rows should sum to 1
    # i.e. divide all values in a row by the row's sum
    prob_matrix = np.zeros((cat_number, cat_number))
    for rownum in list(range(cat_number)):
        prob_matrix[rownum] = matrix[rownum] / sum(matrix[rownum])

    return prob_matrix


def typeboolmat(types_and_bool):
    cat_number = 12  # edit if changed

    freq = np.zeros((cat_number, 2), int)  # col1 for True, col2 for False
    for element in types_and_bool:
        # count types for start or end == True
        if element[1]:
            for x in element[0]:
                freq[x][0] += 1
        # count types for start or end == False
        if not element[1]:
            for x in element[0]:
                freq[x][1] += 1
    # probabilities (row sums to 1)
    probmat = np.zeros((cat_number, 2))
    for rownum in list(range(cat_number)):
        probmat[rownum] = freq[rownum] / sum(freq[rownum])

    return probmat
