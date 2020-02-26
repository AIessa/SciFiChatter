# import modules
import random
from project import gen_retrieve
from project import fill_in


# functions used for dialogue generation ###############################################################################

def next_speaker(current_phrase, end_mat):
    current_speaker = current_phrase.get_speaker()
    other_speaker = 'P' if current_speaker == 'CC' else 'CC'
    categories = current_phrase.get_type_nums()
    prob_true = 0
    prob_false = 0
    for c in categories:
        prob_true += end_mat[0][c]
        prob_false += end_mat[1][c]
    if prob_true > prob_false:
        return other_speaker
    else:
        return current_speaker


def formatprint(phrases, i):
    phrase_string = list(phrases['PHRASE'][i])[0]
    speaker = list(phrases['SPEAKER'][i])[0]
    print(speaker+' : '+phrase_string)


def diceroll(level_of_randomness):
        return random.random() < level_of_randomness


#######################################################################################################################
# (top level: generates one 'full' dialogue when called)

def chatter(phrases, transition_prob, output_length, random_increase):
    # initialise sequence of chosen indices (phrases)
    used_indices = []
    randomness_meter = 0.3

    # get start phrase
    first_phrase_row = gen_retrieve.first_phrase(phrases)
    i_current = first_phrase_row.index[0]
    formatprint(phrases, i_current)
    print('first phrase chosen, logging used index: '+str(i_current)+'\n')
    used_indices.append(i_current)

    # loop until approximate length is reached
    for x in range(output_length):
        # decide on next speaker based on dialogue history
        speaker = gen_retrieve.decide_speaker(phrases.copy(), used_indices)
        print('next speaker will be: '+str(speaker))

        # possible aliens/random choice
        if diceroll(randomness_meter):  # random choice
            print('dice roll returned True, getting random observation...')
            next_phrase_index = gen_retrieve.random_observation(phrases.copy(), i_current, speaker, used_indices)
            # set probability to 0 for next round
            randomness_meter = 0
        else:  # calculate likely next phrase
            print('calculating next phrase...')
            next_phrase_index = gen_retrieve.next_phrase_a(phrases.copy(), i_current, transition_prob, speaker, used_indices)
            # increase randomness probability for next round
            randomness_meter += random_increase

        # update params
        formatprint(phrases, next_phrase_index)
        i_current = int(next_phrase_index)
        print('next phrase chosen, logging index: '+str(i_current)+'\n')
        used_indices.append(i_current)

    speaker_sentence_pairs = []
    for index in used_indices:
        row = phrases[phrases['i']==int(index)]
        print(list(row['SPEAKER'])[0]+' : '+list(row['PHRASE'])[0])
        speaker_sentence_pairs.append((list(row['SPEAKER'])[0], list(row['PHRASE'])[0]))

    # fill-in step
    dialogue = fill_in.fill_all_in(speaker_sentence_pairs)

    # print finished dialogue
    for sp, sent in dialogue:
        print(sp+':\t'+sent)

    # save to file if you want...


def chatter_random(phrases, approx_length):
    used_indices = []

    ind_not_cc = phrases[phrases['SPEAKER'].apply(lambda x: (x != 'CC'))].index
    ind_not_p = phrases[phrases['SPEAKER'].apply(lambda x: (x !='P'))].index
    phrases_cc = phrases.copy()
    phrases_cc.drop(ind_not_cc, inplace=True)
    phrases_p = phrases.copy()
    phrases_p.drop(ind_not_p, inplace=True)

    speaker = 'CC'
    for x in range(approx_length):
        if speaker == 'CC':
            choice_index = phrases_cc['i'].sample(1)
            if diceroll(0.8):
                speaker = 'P'
            phrases_cc.drop(choice_index, inplace=True)
        else:
            choice_index = phrases_p['i'].sample(1)
            if diceroll(0.8):
                speaker = 'CC'
            phrases_p.drop(choice_index, inplace=True)
        formatprint(phrases, choice_index)
        used_indices.append(choice_index)

    speaker_sentence_pairs = []
    for index in used_indices:
        row = phrases[phrases['i'] == int(index)]
        print(list(row['SPEAKER'])[0] + ' : ' + list(row['PHRASE'])[0])
        speaker_sentence_pairs.append((list(row['SPEAKER'])[0], list(row['PHRASE'])[0]))

    # fill-in step
    dialogue = fill_in.fill_all_in(speaker_sentence_pairs)

    # print finished dialogue
    for sp, sent in dialogue:
        print(sp + ':\t' + sent)

    # save to file if you want
