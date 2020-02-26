import re
import numpy as np
import random


# get lines from transcript
def parse_transcript(path):
    transcript = []

    with open(path) as fh:

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
                if not current_stamp is None:
                    try:
                        transcript.append([current_person, current_text])
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

    return transcript


# normalize phrase
def normalize_phrase(phrase):
    # flag_types:
    countdown = (r'3, 2, 1, 0|([0-9]|[a-z]|[A-Z])+ (seconds|minutes|hours)', 'countdown ')
    temperature = (r'-?[0-9]+°', 'x degree ')  # for generation: '-?[1-9][0-9]?[0-9]?°' is more realistic
    speed = (r'[0-9]+ feet per second', 'x fps ')
    distance = (r'[0-9]+ \[nautical miles\]', 'x miles ')
    glossary = (r'\[glossary:(.*?)(\|.+)?\]', r'\1 ')
    time = (r'[0-9]+ (hours)?(,|plus) [0-9]+ (minutes)?(,|plus) [0-9]+ (seconds)?|\[time:.*\]', 'x minutes ')
    percentage = (r'[0-9][0-9]?(( |-)[0-9][0-9]?[0-9]?)? (\[percent\]|percent)', 'x percent ')
    degrees = (r'[0-9][0-9]? (\[degrees\]|degrees)', 'x degrees ')
    alphabet = (r'Alpha|Bravo|Charlie|Delta|Echo|Foxtrot|Golf|Hotel|India|Juliet|Kilo|Lima|Mike|November|Oscar|Papa|Quebec|Romeo|Sierra|Tango|Uniform|Victor|Whiskey|Xray|Yankee|Zulu', 'alphabet')
    location = (
        r'Flor(ida)?|Johannesburg|Washington|Tech|California|(Area [0-9]|Mississippi)|Hawaii|Perth|Rockingham|Africa|Area',
        'Amsterdam ')
    name = (
        r'California Com Tech|Mercury|Texas|Seven|Gordo|California Cap Com|Friendship (Seven|7)|Dog|Easy|(Cap)? Com|Z (Cal)?|CapCom|Muchea|Kano|Charlie|R (c|C)al|John|Guaymas|Indian|Bermuda|Steelhead|Aeromed|Cape|Canary|(Indian)? Cap Com|(Indian)? Com Tech|Indian Surgeon|Woo?(mm?|n)era|Canaveral|Zan(zibar)?|Canton',
        ' Mary ')
    number = (r'[0-9]+(.[0-9]+)?', 'x ')
    space_object = (r'(t|T)he moon|Sirius|Canopus|Orion|Pleiades', 'Vulcan ')
    # also remove random html stuff & double Mary
    html = (r'<.+>|</.+>', '')
    justmary = (r'Mary( )*Mary', 'Mary')
    singlespaces = (r'  ', ' ')
    weird_brackets = (r'\]|\[|\(|\)', '')
    no_semicolons = (r';', '.')

    flag_types = [space_object, distance, countdown, temperature, speed, name, glossary, time, percentage, degrees,
                  alphabet, location, number, html, justmary, singlespaces, weird_brackets, no_semicolons]

    # iterate through flags to find & replace all with flag marker
    for flag in flag_types:
        if bool(re.search(flag[0], phrase)):
            phrase = re.sub(flag[0], flag[1], phrase)

    if phrase[0] == ' ':
        phrase = phrase[1:]

    return phrase


# categorize phrase_type
# there are 12 right now
# IF CHANGED, make sure to edit probabilities.py; also update cat-list in type2vec
def categorize_phrase(phrase):
    # Mary , this is Mary .
    contact_request = (
        r'(mary , )+(this is mary \.)?|(^this is mary)|how me\?|(do you|ready to) copy|hello(,)? mary', 'contact_request')
    contact_answer = (r'mary , mary \.|mary \.|loud and clear|i copy|fine|very well|sounds good|garbled|read you|(i)? (do not|don\'t|did not) (receive|copy|read)', 'contact_answer')
    #
    info_request = (r'what (is|are)|what\'s your|how (did|are|now)|report|is that', 'info_request')
    #
    action_request = (r'(can|would|could) you|go ahead|please|continue (with)?|recommend that|you will have to|standby for|standby|wait', 'action_request')
    repeat_request = (r'say again|repeat|rather garbled|you were broken up|did not receive you', 'repeat_request')
    action_answer = (r'understand.|good.|that(\'s| is) affirm(ative)?|affirmative|check|okay|all right|rog(er)?|fine|will do|very well|standing by|sounds good', 'action_answer')
    #
    confirmation_request = (r'have you|are you|do you|does it|did you|got it\?', 'confirmation_request')
    confirmation = (r'(that(\'s| is))? (affirmative|correct).|i believe so|go ahead|good.|recommend.|should be|yes|negative|here we go|all right', 'confirmation')
    #
    or_question = (r'is this .* or .*\?', 'or_question')
    #
    observation = (r'(the .* is .*\.)|there are|(they .*\.)|beautiful|(i|you) (can(\'t)?)? see|view|sight|look(s|ing)|i saw', 'observation')
    #
    status_info = (r'you (have|look)|holding|is (normal|very|good|on its way|off|on|in|out|next|excellent)|cabin pressure|(fuel|oxygen) (is|x)|x (degree(s)?|knots|percent)|countdown|plus|ready for|here we go|you are|looking good|getting close|you\'re|looks good|everything looks|i (do|do not|now)? have|i am|i\'m|we\'re|my condition|operating normally|there is', 'status_info')
    #
    finisher = (r'over\.|out\.','finisher')


    categories = [status_info, contact_request, confirmation_request, repeat_request, contact_answer, confirmation, info_request,
                  action_answer, action_request, or_question, observation, finisher]

    # lowercase & check phrases
    cat_choices = []
    for cat in categories:
        if bool(re.search(cat[0], phrase.lower())):
            cat_choices.append(cat[1])

    # edit cat choices and choose maximum 2:
    if len(cat_choices) > 2:
        cat_choices = random.choices(cat_choices, k=2)

    return cat_choices


# type to binary vector:
def type2vec(chosen_cat):
    categories = ['status_info', 'contact_request', 'confirmation_request', 'repeat_request', 'contact_answer', 'confirmation',
                  'info_request', 'action_answer', 'action_request', 'or_question', 'observation', 'finisher']
    cat2int = dict(zip(categories, list(range(0, len(categories)))))

    vec = np.zeros((len(categories),), int)
    for c in chosen_cat:
        vec[cat2int[c]] = 1

    return vec


