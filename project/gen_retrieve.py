# import modules
from __future__ import division
import numpy as np


# retrieval ############################################################################################################

# helper function for next_phrase_a
def get_phrase_subset(phrases, i_current, speaker, used_indices):
    print('GETTING APPROPRIATE PHRASE SUBSET')
    # for ref: get categories of previous phrases
    used_categories = [list(phrases[phrases['i'] == int(index)]['TYPECATS'])[0] for index in used_indices]
    print(used_categories)

    # for ref: previous speaker
    prev_speaker = list(phrases[phrases['i'] == int(i_current)]['SPEAKER'])[0]

    # remove phrases that don't have next speaker  as 'SPEAKER'
    indexNames = phrases[phrases['SPEAKER'].apply(lambda x: (x != speaker))].index
    phrases.drop(indexNames, inplace=True)
    print('phrases with right speaker: ' + str(len(phrases)))

    # remove phrases that have been used previously:
    indexNames = phrases[phrases['i'].apply(lambda x: x in used_indices)].index
    phrases.drop(indexNames, inplace=True)
    print('phrases without repeating: ' + str(len(phrases)))

    # avoid repeating classes 'contact request' and 'contact answer' (4: contact answer, 1: contact request
    if len(used_categories) > 1 and (4 in used_categories[-1]):  # last phrase was contact answer
        if (1 or 4) in used_categories[-2]:  # previous to last was contact request or answer
            indexNames = phrases[phrases['TYPECATS'].apply(lambda x: 1 in x or 4 in x)].index
            phrases.drop(indexNames, inplace=True)
            print('phrases not contact answer or request: ' + str(len(phrases)))
        else:
            pass
    else:
        pass

    # if next_speaker != previous speaker, all phrases with 'ISSTART' == False must be filtered out
    if prev_speaker != speaker:
        indexNames = phrases[phrases['ISSTART'].apply(lambda x: x == False)].index
        phrases.drop(indexNames, inplace=True)
        print('phrases with ISSTART: ' + str(len(phrases)))
    else:
        indexNames = phrases[phrases['ISSTART'].apply(lambda x: x == True)].index
        phrases.drop(indexNames, inplace=True)
        print('phrases without ISSTART ' + str(len(phrases)))

    return phrases


# fetch next phrase
def next_phrase_a(phrases, i_current, transition_probabilities, next_speaker, used_indices):
    # check for repeat request (cat 3), in which case repeat most recent phrase of 'next_speaker' ######################
    last_cats = list(phrases[phrases['i'] == int(used_indices[-1])]['TYPECATS'])[0]
    if 3 in last_cats:
        last_speakers = [(list(phrases[phrases['i'] == int(i)]['SPEAKER'])[0], int(i)) for i in used_indices]
        repetition_index = [ind for (sp, ind) in last_speakers if sp == next_speaker][-1]
        print('IS REPEAT REQUEST')
        return repetition_index

    # unless repeat request, proceed with calculation ##################################################################
    else:

        # get current row
        current_row = phrases[phrases['i'] == int(i_current)]

        # remove inappropriate options from set for next_choice
        sub_df = get_phrase_subset(phrases, i_current, next_speaker, used_indices)

        # get vector of (joint) transition probabilities to each dialogue act category, given all categories of current:
        current_cat = list(current_row['TYPECATS'])[0]
        print(current_cat)

        trans2cats = np.zeros(len(transition_probabilities))
        for i1 in current_cat:  # matrix index of "from" category, e.g. [0,5] = current phrase has cat. indices 0 & 5
            for i2 in range(
                    len(trans2cats)):  # go through all possible category indices, 0->0, 0->1, ... & 5->0, 5->1...
                value = transition_probabilities[i1][i2]
                # print(str(i1)+', '+str(i2) + ': '+str(type(value)))
                trans2cats[i2] += value
        # normalise trans2cats:
        trans2cats = trans2cats / len(current_cat)
        print(trans2cats)

        # METHOD: Choose phrase that maximises fitness
        # calculate fitness of all phrases (that are allowed, hence the subset of rows), given transition vector!
        # add col with fitness values (sum of values in v = typevec * trans2cats)
        new_col = sub_df['TYPEVEC'].apply(lambda x: sum(np.multiply(x, trans2cats)))
        new_df = sub_df.assign(FITNESS=new_col.astype(float))

        # pick (get top 10 rows with highest fitness values & choose random i)
        fittest_rows = new_df.nlargest(10, 'FITNESS')
        choice_index = fittest_rows['i'].sample(1)
        # print(new_df.loc[choice, :])
        # print(next_speaker + ' : ' + str(new_df.loc[choice_index, 'PHRASE']))
        return choice_index


# either generates alien intermission or fetches a random observation
def random_observation(phrases, i_current, next_speaker, used_indices):

    # remove inappropriate options from set for next_choice
    sub_df = get_phrase_subset(phrases, i_current, next_speaker, used_indices)
    # only observations (cat 10)
    indexNames = sub_df[sub_df['TYPECATS'].apply(lambda x: not (10 in x))].index
    sub_df.drop(indexNames, inplace=True)
    # choose random
    choice_index = sub_df['i'].sample(1)

    return choice_index


# generates "appropriate" conversation start (mostly random, avoiding something like "Over.")
def first_phrase(phrases):
    # column "ISSTART" should be True & appropriate categories chosen (arbitrarily) have indices
    # ['contact request' = 1, 'observation' = 10, 'status info' = 0]
    start_rows = phrases[
        (phrases.ISSTART == True) & (phrases.TYPECATS.apply(lambda x: (0 in x) or (1 in x) or (10 in x)))]
    # from chosen return random
    return start_rows.sample(1)


# decide on speaker for next phrase based on dialogue history
def decide_speaker(phrases, used_indices):
    # if last two were same speaker, automatically change
    last_speaker = list(phrases[phrases['i'] == int(used_indices[-1])]['SPEAKER'])[0]
    prev2last_speaker = list(phrases[phrases['i'] == int(used_indices[-1])]['SPEAKER'])[0] if len(used_indices)>1 else ''
    last_isend = list(phrases[phrases['i'] == int(used_indices[-1])]['ISEND'])[0]

    if len(used_indices) > 1:
        if last_speaker == prev2last_speaker:
            return 'P' if str(phrases['SPEAKER'][used_indices[-1]]) == 'CC' else 'CC'
    else:
        # check whether last phrase was originally an end phrase
        if last_isend:  # if yes, switch speaker
            return 'P' if last_speaker == 'CC' else 'CC'
        else:  # stay with current speaker
            return 'CC' if last_speaker == 'CC' else 'P'


