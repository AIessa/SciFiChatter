# import modules

from nltk import sent_tokenize
from collections import Counter
import pandas as pd
import pickle

from project import phrase_obj
from project import preprocessing
from project import probabilities as prob


if __name__ == '__main__':
    # parse transcript
    # ADJUST SOURCE PATH!
    transcript_path = '/Users/Alessandra/Desktop/ANLP/SciFiChatter/data/ma6/transcripts/TEC'
    transcript_parsed = preprocessing.parse_transcript(transcript_path)  # is list: [speaker, line]
    print("\ntranscript found and parsed\n")

    # create phrase object collection
    print("processing phrases... producing templates... dialogue act classification...\n")
    phrases = {}
    indexer = 0
    phrase_garbage = []  # to record phrases that are excluded from generator, because they are not in any category
    for line in transcript_parsed:
        speaker = line[0]
        sentences = sent_tokenize(line[1])
        for i, s in enumerate(sentences):
            # initialize new phrase object
            phr = phrase_obj.Phrase(indexer, s, speaker)

            # assign speaker_change_bools
            start = True if (i == 0) else False
            end = True if (i + 1 == len(sentences)) else False
            speaker_change = [start, end]

            # normalize and get types
            template = preprocessing.normalize_phrase(s)
            type_choices = preprocessing.categorize_phrase(template)
            if not type_choices:
                phrase_garbage.append(template)  # record garbage

            # populate
            type_vector = preprocessing.type2vec(type_choices)
            type_nums = [i for i, val in enumerate(type_vector) if val == 1]

            # add variables to phrase object
            phr.setup(template, type_vector, type_nums, speaker_change)

            # complete phrase object to dict -------------
            phrases[indexer] = phr

            # increment indexer --------------------------
            indexer += 1

    #######################
    # EVAL
    print("evaluating dialogue act classification: ")
    print(str(len(phrase_garbage)) + " sentences could not be classified, will be excluded.")
    print(str(len(phrases)) + " sentences were transformed into templates and classified.")
    cc = [phrases[i] for i in phrases if phrases[i].get_speaker() == 'CC']
    p = [phrases[i] for i in phrases if phrases[i].get_speaker() == 'P']
    cc_types = Counter([str(phr.get_type_nums()) for phr in cc])
    p_types = Counter([str(phr.get_type_nums()) for phr in p])
    print(str(len(cc)) + " phrases assigned to CC (character x).")
    print(cc_types)
    print(str(len(p)) + " phrases assigned to P (character y).")
    print(p_types)
    print('\n')
    #######################

    # create probability matrices
    print("calculating probabilities for speaker changes and dialogue act sequences...\n")
    trans_prob_mat = prob.transmatrix(
        [phrases[i].get_type_nums() for i in sorted(phrases) if len(phrases[i].get_type_nums())])
    # starttype_prob = prob.typeboolmat([(phrases[i].get_type_nums(), phrases[i].is_starter()) for i in sorted(phrases)])
    # endtype_prob = prob.typeboolmat([(phrases[i].get_type_nums(), phrases[i].is_ending()) for i in sorted(phrases)])

    #######################
    # EVAL
    print("probability distribution for dialogue act sequences (bi-grams):\n")
    print("NOT YET ADDED IN CODE\n\n")

    #######################

    # turn dict of phrases into a pandas data frame to store & load to generate sentences (without re-running this code)
    phrase_dict = {}
    for i in phrases:
        p = phrases[i]
        phrase_dict[i] = [i, p.get_speaker(), p.get_template(), p.get_types(), p.get_type_nums(), p.is_starter(), p.is_ending()]
    column_names = ['i', 'SPEAKER', 'PHRASE', 'TYPEVEC', 'TYPECATS', 'ISSTART', 'ISEND']
    df = pd.DataFrame.from_dict(phrase_dict, orient='index', columns=column_names)
    print(df.head(10))

    # components saved in directory: model_components
    # ADJUST TARGET PATH!
    # save model with pickle (highest protocol)
    df.to_pickle(path='/Users/Alessandra/Desktop/ANLP/SciFiChatter/model_components/phrases.pkl')
    pickle.dump(trans_prob_mat, open('/Users/Alessandra/Desktop/ANLP/SciFiChatter/model_components/transition_probabilities.pkl', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
    # pickle.dump(starttype_prob, open('/Users/Alessandra/Desktop/ANLP/SciFiChatter/model_components/is_start_probabilities.pkl', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
    # pickle.dump(endtype_prob, open('/Users/Alessandra/Desktop/ANLP/SciFiChatter/model_components/is_end_probabilities.pkl', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)

