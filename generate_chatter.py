"""
Contains: main
    - Generate chatter dialogue between two characters
    - Class Person

Use: can run without input, can change variables in main (but not recommended for current implementation)

@author: Claudia A. Libbi
"""

import phrases
import re
import random


class Person:

    def __init__(self, name):
        self.name = name
        self.initiative_count = 0  # how often did person start dialogue
        self.memory = []  # stack of phrases used
        self.phrases = None  # phrase structures that explorer is allowed to use

    # define person, i.e. assign phrase objects it can use depending on choice of character
    def setup(self, transcript_phrases, person_code):
        char_phrases = {}
        for i, phrase in transcript_phrases.items():
            if phrase.get_info()['speaker'] == person_code:
                char_phrases[i] = phrase
        self.phrases = char_phrases

    # update stack of lines that character has generated since instantiation or last time cleared
    def update_memory(self, said):
        self.memory += said

    # clears dialogue history of person, but keeps setup
    def clear(self):
        self.memory = []
        self.initiative_count = 0

    # should be called if character's turn in dialogue generator
    # TODO: implement line choice & generation
    def generate_line(self, chatter_memory):

        if not chatter_memory:
            # if chatter_memory is empty, use conversation starter!
            self.initiative_count += 1
            pass

        else:
            # generate line based on chatter_memory[-1], self.memory and self.phrases
            pass

        line = ''
        self.update_memory(line)
        return line

    # temporary random line generator
    def generate_random(self):
        while True:
            # try random lines (break if 'new' line found)
            key = random.sample(list(self.phrases), 1)[0]
            line = (self.phrases[key]).get_info()["original"][2]
            if not (line in self.memory):
                self.update_memory(line)
                return line


def generate_dialogue(person1, person2):
    print('\n - CHATTER START - \n')
    memory = []  # stack of generated lines, memory[-1] is what was last said
    steps = 0  # how many lines have been generated
    speaker = random.choice([person1, person2])  # current speaker
    last_said = ''
    while True:
        # current speaker generates line:
        # TODO: Change when generate_line(memory) is implemented
        line = speaker.generate_random()
        print(speaker.name + ':\t\t'+line)

        # update tracking:
        steps += 1
        memory += line
        speaker = person1 if (speaker == person2) else person2  # switch speaker

        # conversation end check
        # TODO: Match expression should be replaced by phrase property check, s.t. phrase.get_info()['flag'] == 'END'
        if bool(re.match(r'.*Rog(er)?\.$', line)):
            print('\n- CHATTER END -\n')
            break


if __name__ == "__main__":
    # 'ma6': Mercury 6 (Description: First American to reach earth orbit)
    phrases = phrases.phrasify(phrases.make_transcript('ma6'))
    print("Generating radio chatter based on the 'Mercury 6' NASA mission.\n")

    # choice of characters
    characters = ['CC', 'P']
    print("Dialogue originally between CC (Capsule Communicator/Astronaut) and P (Astronaut)")

    # TODO: Adapt phrases to remove all irrelevant characters (function to be implemented in phrases.py)

    # create instances of characters
    explorer = Person('COMMUNICATIONS')
    explorer.setup(phrases, 'CC')
    commander = Person('EXPLORER')
    commander.setup(phrases, 'P')
    print("Instances created for interaction between explorer and communications.")
    print("\nReady for dialogue generation (currently set to random):")

    # generate dialogue
    generate_dialogue(explorer, commander)
