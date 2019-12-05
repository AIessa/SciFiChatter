"""
Contains: nlp for phrases in transcript
    - Tagging
    - Categorization

Use: by phrases.py to setup phrase objects (??? Not sure yet how this will work)
    Functions take a phrase object & return tags to populate phrase values (not a list of!)

@author: Claudia A. Libbi
"""

# TODO: Everything lol (NLP and also phrase choice logic, probably in separate script)

import re
import spacy


def normalize_phrase(phrase_text):

    # flag_types:
    temperature = (r'-?[0-9]+°', '/TEMPERATURE/')  # for generation: '-?[1-9][0-9]?[0-9]?°' is more realistic
    speed = (r'[0-9]+ feet per second', '/SPEED/')
    glossary = (r'\[glossary:.+\]', '/GLOSSARY/')
    time = (r'[0-9]+ (hours)?(,|plus) [0-9]+ (minutes)?(,|plus) [0-9]+ (seconds)?|\[time:.*\]', '/TIME/')
    percentage = (r'[0-9][0-9]?(-[0-9][0-9]?[0-9]?)? (\[percent\]|percent)', '/PERCENTAGE/')
    countdown = (r'([0-9]|[a-z]|[A-Z])+ (seconds|minutes|hours)', '/COUNTDOWN/')
    degrees = (r'[0-9][0-9]? (\[degrees\]|degrees)', '/DEGREES/')
    location = (r'(Area [0-9]|Mississippi) Delta|Hawaii|Area Hotel', '/LOCATION/')
    name = (r'Friendship Seven|R Cal|John|Guaymas|Bermuda|Steelhead|Aeromed|Cape|Canary|(Indian)? Cap Com|(Indian)? Com Tech|Indian Surgeon|Woo?mm?era|Canaveral|Zanzibar|Canton', '/NAMES/')

    flag_types = [temperature, speed, glossary, time, percentage, countdown, degrees, location, name]

    # iterate through flags to find & replace all with flag marker
    seen_flags = []
    for flag in flag_types:
        if bool(re.match(flag[0], phrase_text)):
            seen_flags += flag[1]
            phrase_text = re.sub(flag[0], flag[1], phrase_text)

    return phrase_text, seen_flags


def phrase_nlp(phrase):
    # replace observed objects with object-flags
    # The OBJ is DESCR. (DESCR = ADJ ...)pass
    # I can (still) see (clear) OBJ-PHR. (OBJ-PHR = OBJ WHERE | ADJ OBJ ...)
    # I do not have any of the OBJ identified as yet.
    pass


def categorize_phrase(phrasebook):
    # Is status question (Have you completed your X? Do you read? or 'Are you going through the X?')
    q_status_pattern = r'Have you .*\?|Are you .*\?|Do you .*\?|(H|h)ow me\?'
    # Is status answer (require keyword from status question,
    # e.g. 'do you read' -> 'Loud and clear.' or 'oxygen' -> 'Oxygen is [percent])
    q_status_answer_pattern = r'Loud and clear.|Understand.|(T|t)hat(\'s| is) affirmative.'

    # Is OR question (Is this X or Y?)
    q_or_pattern = r'Is this .* or .*\?'
    # Is OR answer

    # Is information request (Would you give me X?)
    i_request_pattern = r'What are the .*\.|(Could|Can|Would) you (give)? .*\?'
    # Is information request answer
    i_request_answer_pattern = r'Okay'

    # Is action request (Continue with X | Standby for X)
    a_request_pattern = r'Continue with .*\.|Standby for .*\.'
    # Is action request answer (Roger. (Repeat request in infinitive (verb) e.g. switching to X))
    a_request_answer_pattern = r'Roger.'

    # Is observation: 'They ...', 'Area 3 Delta is [hours-minutes-seconds]
    observation_pattern = r'The .* is .*\.|They .*\.|.* is .*\.|I can see .*\.'

    # Is simple_confirmation: 'yes', 'roger', 'rog'

    # Is greeting / contact request: 'Hello Y. X. Over'
    # Is contact request answer: 'X, this is Y. Do you read? Over.'
    identification_pattern = r'This is .*\.|.*, this is .*\.'
    pass


def parse_phrase(phrase):
    nlp = spacy.load("en_core_web_sm")
    tagged_phrase = nlp(phrase)
    # ideally, can I add tags? I want flag tags
    """
    for token in tagged_phrase:
        print(token.text, token.pos_, token.dep_)
        
    """
