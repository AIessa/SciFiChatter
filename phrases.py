"""
Contains:
    Transcript class, make_transcript function
    Phrase class, phrasify function

Use example: Getting the collection of phrases from TEC (transcript file) of mission 'ma6'
phrases = phrasify(make_transcript('ma6'))

@author: Claudia A. Libbi
"""

import re
import nlp_phrases


# make transcript object
# TODO: Remove self.speakers, update_speakers() & get_speakers() (after alternative dialogue generator is implemented)
class Transcript:

    def __init__(self, mission):
        self.name = mission
        self.path = '/Users/Alessandra/Desktop/SciFiChatter/missions/' + mission + '/transcripts/TEC'
        self.meta = '/Users/Alessandra/Desktop/SciFiChatter/missions/' + mission + '/transcripts/_meta'
        self.lines = []  # list of lines
        self.speakers = {}  # dictionary of speakers, each speaker has list of lines

    def print_lines(self):
        with open(self.path) as fh:
            for line in fh:
                print(line)

    def update_lines(self, line):
        self.lines = self.lines + [line]

    def update_speakers(self, person, text):
        if person in self.speakers:
            self.speakers[person] = self.speakers[person] + [text]
        else:
            self.speakers[person] = [text]

    def run_through(self):
        with open(self.path) as fh:

            current_stamp = None
            current_person = None
            current_text = ''

            for line in fh:
                # ignore empty lines or comments
                if not line.strip() or line.strip()[0] == "#":
                    continue
                # ignore metadata about pages etc.
                elif line[0] == "_":
                    continue
                # recognize timestamps
                elif line[0] == "[":
                    # update dictionary with current entry:
                    if not current_stamp == None:
                        try:
                            self.update_lines([current_stamp, current_person, current_text])
                            self.update_speakers(current_person, current_text)
                        except:
                            print('AAh darn something here was not parsed right??')
                            break
                    # change current stamp & reset variables:
                    current_stamp = line[1:].split("]")[0]
                    current_person = None
                    current_text = ''
                else:
                    # get text content and person, if speech start
                    if bool(re.match('([A-Z]|[0-9])+: .*', line)):
                        current_person = line.split(':', 1)[0]
                        current_text += (line.split(':', 1)[1]).strip()
                    else:
                        current_text += ' ' + line.strip()

    def get_speakers(self):
        return self.speakers

    def get_lines(self):
        return self.lines


# DONE
def make_transcript(mission_name):
    try:
        t = Transcript(mission_name)
        t.run_through()
    except IndexError:
        print("Please pass a file to reformat")
    return t


# Make phrase objects containing grammar etc.
# TODO: Finish self.nlp() as soon as nlp_phrases.py is implemented
class Phrase:

    def __init__(self, orig_phrase, i):
        self.original = orig_phrase  # [timestamp, speaker, text]
        self.i = i  # index of phrase in order of original transcript
        self.speaker = orig_phrase[1]
        self.responds2 = None
        # other properties configured using nlp_phrases.py:
        self.category = None
        self.grammar = None
        self.flags = None

    def response2(self, phrase_obj):
        self.responds2 = phrase_obj

    def nlp(self):
        original_text = self.original[2]
        # normalize
        normalized, self.flags = nlp_phrases.normalize_phrase(original_text)

        # parse???
        # self.grammar = nlp_phrases.phrase_nlp() or nlp_phrases.parse()

        # assign phrase category/categories
        # self.category = nlp_phrases.categorize_phrase(normalized) <- or should it also take the fully parsed version?

        pass

    def get_info(self):
        return {'original': self.original,
                'i': self.i,
                'speaker': self.speaker,
                'responds2': self.responds2,
                'category': self.category,
                'grammar': self.grammar,
                'flags': self.flags}


# DONE
def phrasify(transcript_obj):
    phrases = {}  # map of phrase objects indexed by i

    for i, line in enumerate(transcript_obj.lines):
        new_phrase = Phrase(line, i)
        # update phrase object: add reference to previous phrase
        if i == 0:
            print('\nPhrasifying transcript...')
        else:
            new_phrase.response2(phrases[i - 1])
        # update phrase object: apply nlp methods for tagging and categorisation
        new_phrase.nlp()
        # update phrase map:
        phrases[i] = new_phrase

    print('Done.\n')
    return phrases


# TODO: implement a function to get a subset of phrases of just 2 specified speakers, e.g. 'CC' & 'P' (low priority)
"""
ideas: 
- allow summarizing characters, e.g. set P == C & update lines & people 
- delete people & only keep useful dialogue blocks (recursive: if deleting line at i, delete i-1 & i+1 iff relevant to i)
"""

"""
# TEST:
if __name__ == "__main__":
    phrases = phrasify(make_transcript('ma6'))
    print(phrases[0].get_info())
"""