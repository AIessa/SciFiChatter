# import modules

import pandas as pd
import pickle

from project import generator

if __name__ == '__main__':
    # load & import model components:
    phrases = pd.read_pickle(
        "model_components/phrases.pkl")  # column_names = ['SPEAKER', 'PHRASE', 'TYPEVEC', 'TYPECATS', 'ISSTART', 'ISEND']
    transition_prob = pickle.load(open('model_components/transition_probabilities.pkl', 'rb'))
    # not currently in use:
    # start_prob = pickle.load(open('model_components/is_start_probabilities.pkl', 'rb'))
    # end_prob = pickle.load(open('model_components/is_end_probabilities.pkl', 'rb'))
    print(len(phrases))
    # initial filer step: remove phrases that have no assigned categories...
    indexNames = phrases[phrases['TYPECATS'].apply(lambda x: len(x) == 0)].index
    phrases.drop(indexNames, inplace=True)
    print("Number of phrases after filtering: " + str(len(phrases)))

    n = 30
    random_increase = 0.5
    generator.chatter(phrases, transition_prob, n, random_increase)

    # generator.chatter_random(phrases, n=30)
