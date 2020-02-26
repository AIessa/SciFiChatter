# import modules
import random as ran
import re


# filling in the complete template #####################################################################################
def path2list(textfile):
    vocab = []
    with open(textfile, 'r') as f:
        for line in f.readlines():
            vocab.append(str(line))
    return vocab


def namegame(speaker_sentence_pairs):
    # import potential spaceship names, assign 2 randomly
    spaceship_names = path2list('/Users/Alessandra/Desktop/ANLP/SciFiChatter/data/spaceship_names.txt')
    actors = ran.sample(spaceship_names, 3)  # third is not participating in dialogue
    name_assignment = dict(zip(['p', 'cc', 'other'], actors))
    print(name_assignment['p'])
    print(name_assignment['cc'])
    print(name_assignment['other'])

    named_dialogue = []
    for (speaker, sentence) in speaker_sentence_pairs:
        if 'Mary' in sentence:
            sentence = re.sub(r'Mary( )+Mary', 'Mary', sentence) # make sure no double Marys
            sentence = re.sub(r'Mary flight', 'Mary', sentence) # weird exception

            #######
            # THIRD PERSON:
            newname = name_assignment['other'].strip()

            pattern = r'Mary( will)'
            if bool(re.search(pattern, sentence)):
                sentence = re.sub(pattern, newname+'\1', sentence)

            pattern = r'(they will ([a-z] )*)Mary( ?.)'
            if bool(re.search(pattern, sentence)):
                sentence = re.sub(pattern, '\1'+newname+'\2', sentence)

            # DIALOGUE PARTNER:
            newname = name_assignment['cc' if speaker != 'CC' else 'p'].strip()

            # Mary after 'Mary, ' & before '.'
            pattern = r'(Mary ?, )Mary ?(.)'
            if bool(re.search(pattern, sentence)):
                sentence = re.sub(pattern, r'\1'+newname+r'\2', sentence)

            # Mary after sentence start and before . or ,
            pattern = r'^Mary ?(,|.)'
            if bool(re.search(pattern, sentence)):
                sentence = re.sub(pattern, newname+r'\1', sentence)

            pattern = r'((Roger|Hello),? )Mary'
            if bool(re.search(pattern, sentence)):
                sentence = re.sub(pattern, r'\1'+newname, sentence)

            pattern = r'(, )Mary ?(.)'
            if bool(re.search(pattern, sentence)):
                sentence = re.sub(pattern, r'\1'+newname+r'\2', sentence)

            #######
            # SELF:
            newname = name_assignment['cc' if speaker == 'CC' else 'p'].strip()

            # this is Mary
            pattern = r'((t|T)his is )Mary ?'
            if bool(re.search(pattern, sentence)):
                sentence = re.sub(pattern, r'\1'+newname, sentence)

            else:
                # any other instance defaults to "other"
                sentence = re.sub('Mary', name_assignment['other'].strip(), sentence)

        else:
            pass

        # Rename speaker
        if speaker == 'CC':
            name = name_assignment['cc'].strip()
        elif speaker == 'P':
            name = name_assignment['p'].strip()
        else:
            name = name_assignment['other'].strip()
        named_dialogue.append((name, sentence))

    return named_dialogue


def replace_generic_flags(line):
    # remove doubles, i.e. all 'x x' to 'x'
    line = re.sub(r'x( )*x', 'x', line)

    # replace countdowns
    if 'countdown' in line:
        replacer = ran.choice(['3, 2, 1, 0', 'countdown', 'x seconds', 'x minutes', 'x hours'])
        if 'x' in replacer:
            replacer = replacer.replace('x', str(ran.randrange(2, 60, 1)))
        line = line.replace('countdown', replacer)

    # replace temperatures
    if 'x degree' in line:
        value = ran.randrange(-10000, 10000)
        if (value > 1) and (value < -1) and (value != 0):
            line = line.replace('x degree', str(value) + ' degrees')
        else:
            line = line.replace('x degree', str(value) + ' degree')

    # replace degrees (not temperature)
    line = line.replace('x degrees', str(ran.randrange(2, 100)) + ' degrees')

    # replace percent
    line = line.replace('x percent', str(ran.randrange(1, 100)) + ' percent')

    # replace speed
    line = line.replace('x fps', str(ran.randrange(10, 1000)) + ' ' + ran.choice(['feet per second', 'fps']))

    # replace distance
    line = line.replace('x miles', str(ran.randrange(10, 10000)) + ' miles')

    # replace time
    if 'x minutes' in line:
        hours = ran.randrange(0, 6)
        replacer = ''
        if hours != 1:
            replacer += str(hours) + ' hours, '
        else:
            replacer += str(hours) + ' hour, '

        minutes = ran.randrange(0, 60)
        if minutes != 1:
            replacer += str(minutes) + ' minutes, '
        else:
            replacer += str(minutes) + ' minute, '

        seconds = ran.randrange(0, 60)
        if seconds != 1:
            replacer += str(seconds) + ' seconds'
        else:
            replacer += str(seconds) + ' second'

        line = line.replace('x minutes', replacer)

    # replace alphabet code (Alpha Bravo...)
    if 'alphabet' in line:
        options = 'Alpha|Bravo|Charlie|Delta|Echo|Foxtrot|Golf|Hotel|India|Juliet|Kilo|Lima|Mike|November|Oscar|Papa|Quebec|Romeo|Sierra|Tango|Uniform|Victor|Whiskey|Xray|Yankee|Zulu'
        line = line.replace('alphabet', ran.choice(options.split('|')))

    # any other number is replaced randomly (x)
    line = line.replace(' x', ' '+str(ran.randrange(1, 60)))
    line = line.replace('x ', str(ran.randrange(1, 60))+' ')

    # clean up double minusses
    line = line.replace('--', '-')

    return line


def rand_replacement(string, to_be_replaced, items):
    return re.sub(to_be_replaced, lambda x: ran.choice(items).strip(), string )


def replace_scifi(speaker_sentence_pairs):
    # 1: count instances of each, retrieve separate
    # Vulcan
    sights = path2list('/Users/Alessandra/Desktop/ANLP/SciFiChatter/data/planets_and_sights.txt')
    # Amsterdam
    locations = path2list('/Users/Alessandra/Desktop/ANLP/SciFiChatter/data/locations_shorter.txt')
    # Technobabble (replacing fly-by-wire, added before problem/check)
    technobabble = path2list('/Users/Alessandra/Desktop/ANLP/SciFiChatter/data/technobabble.txt')
    # Space objects
    objects = path2list('/Users/Alessandra/Desktop/ANLP/SciFiChatter/data/space_objects.txt')

    scified = []
    for speaker, sentence in speaker_sentence_pairs:

        sentence = rand_replacement(sentence, 'Vulcan', sights)
        sentence = rand_replacement(sentence, 'Amsterdam', locations)
        sentence = rand_replacement(sentence, 'fly-by-wire', technobabble)

        # observations: replace first they/They
        observation = r'(the .* is .*\.)|there are|(they .*\.)|beautiful|(i|you) (can(\'t)?)? see|view|sight|look(s|ing)|i saw'
        if bool(re.search(observation, sentence)) and not ('they want' in sentence):
            sentence = re.sub(r'(t|T)hey', ran.choice(objects).strip(), sentence, count=1)

        # technobabble before problem/check
        sentence = re.sub(r'(problem)|(check)', ran.choice(technobabble).strip()+' '+'\1', sentence)

        scified.append((speaker, sentence))

    return scified


def fill_all_in(speaker_phrase_template_sequence):
    # fill in speaker names:
    names_done = namegame(speaker_phrase_template_sequence)

    # fill in sci-fi vocabulary instances:
    scified = replace_scifi(names_done)

    # fill in the left-over "generic" values per line:
    finished = []
    for speaker, sentence in scified:
        finished.append([speaker, replace_generic_flags(sentence)])

    # return filled in to be printed/saved
    return finished