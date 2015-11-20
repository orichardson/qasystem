from nltk import *
from libutils import *

# In order to use these you need to have (from nltk.download() or wherever)
# punkt
# averaged perceptron tagger


def part_of_speech_prefix(begins_with):
    return lambda tag: True if tag[1].startswith(begins_with) else False

#To do:
# Add some metric for finding more relevant nouns and verbs.
# Use a parser to get prepositional phrases directly

def question_process(q):
    text = q['Question'].lower().strip()
    tree = parse(text)[0];

    print(tree)

    words = tree.leaves();
    constr = [];
    q['searchtype'] = 'NP';

    if words[0] == 'how':
        if words[1] == 'many' or words[2] == 'much' :
            constr.append(('QUANTITY', 10))

    elif words[0] == 'where':
        constr.append('LOCATION')
        q['searchtype'] = 'NP'

    elif words[0] == 'what':
        q['searchtype'] = 'NP'

    elif words[0] == 'who':
        constr.append(('PERSON', 10))
        constr.append(('ORGANIZATION', 2))
        q['searchtype'] = 'NP'

    elif words[0] == 'why':
        constr.append(('REASON', 5))

    tagged = pos_tag(word_tokenize(text))
    q['assoc_nouns'] = list(filter(part_of_speech_prefix('NN'), tagged))
    q['assoc_verbs'] = list(filter(part_of_speech_prefix('VB'), tagged))
    q['constraints'] = constr;

#Sample test
#print(question_process("Who did the Queen of England pour mustard on at dinner?"))
