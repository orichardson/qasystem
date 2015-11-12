from nltk import *

# In order to use these you need to have (from nltk.download() or wherever)
# punkt
# averaged perceptron tagger

def find_question_type(q):
    q = q.lower()
    if 'how many' in q: return 'quantity'
    elif 'how much' in q: return 'quantity'
    elif 'how big' in q: return 'size'
    elif 'what kind' in q: return 'description'
    elif 'where' in q: return 'location'
    elif 'what' in q or 'which' in q: return 'identity'
    elif 'who' in q: return 'person_identity'
    elif 'why' in q: return 'reason'
    else: return 'unknown'

def part_of_speech_prefix(begins_with):
    return lambda tag: True if begins_with in tag[1] else False

#To do:
# Add some metric for finding more relevant nouns and verbs.
# Use a parser to get prepositional phrases directly

def question_process(q):
    question_dict = {}
    tagged = pos_tag(word_tokenize(q))
    question_dict['question_type'] = find_question_type(q)
    question_dict['assoc_nouns'] = list(filter(part_of_speech_prefix('NN'), tagged))
    question_dict['assoc_verbs'] = list(filter(part_of_speech_prefix('VB'), tagged))
    return question_dict

#Sample test
#print(question_process("Who did the Queen of England pour mustard on at dinner?"))
