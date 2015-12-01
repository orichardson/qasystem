from nltk import *
from libutils import *
import analyst

# In order to use these you need to have (from nltk.download() or wherever)
# punkt
# averaged perceptron tagger


def part_of_speech_prefix(begins_with):
    return lambda tag: True if tag[1].startswith(begins_with) else False

#To do:
# Add some metric for finding more relevant nouns and verbs.
# Use a parser to get prepositional phrases directly
# Ignore first verb phrase inside an SQ; it's just a connector

# Constraint types:
#  -- prepositional phrases attached to the WH-pronoun
#  -- noun phrases after WHD (Wh-determiner)
#  --

from lawyer import get as lget

QPOSMAP = {'WHNP':'NP', 'WHAVP':'NP', 'WHADJP':'ADJP', 'WHPP':'PP'}
ALL_NOUNS = lget('lexname_constraints').keys() - {'VALUES'}

def question_process(q):
    text = q['Question'].strip()
    tree = parse(text)[0];
    words = tree.leaves();

    # Make a bag of semantic relation for lch_distance via wordnet    
    semanticbag = set()    
    for w in words:
        semanticbag |= lexclass(w, text)
    q['semanticbag'] = semanticbag;
        
    sbarq = tree[0]
    gap = sbarq.subtrees(filter=lambda n:n.label() in QPOSMAP.keys() ).next()
    
    if gap:    
        q['searchtype'] = QPOSMAP[gap.label()];
        
        
        sobj = analyst.Pronoun(Story(), gap[0])
        
        if ismatch(['WDT' 'NN'], gap) :
            sobj.props['lexname'] = lexclass(' '.join(gap[1].leaves()))
        elif ismatch(['WRB', 'JJ']):
            #So this is a 'how tall' question
            sobj.props['lexname'] = {'noun.quantity'}
            
            # w2 = gap.leaves()[1].lower()
            # sobj.props['dimension'] = dimension.fromWord(w2)
            
        elif ismatch(['WRB'], gap) :
            word = gap.leaves()[0].lower()
            
            if word == 'where':
                sobj.props['lexname'] = {'noun.location'}
                sobj.props['ner'] = {'LOCATION'}
            elif word == 'when':
                sobj.props['lexname'] = {'noun.time'}
                sobj.props['ner'] = {'DATE', 'TIME'}
            elif word == 'why':
                sobj.props['lexname'] = {'noun.reason'}
        
        elif ismatch(['WP'], gap) :
            # so there's only one node
            word = gap.leaves()[0].lower()
            if word == 'who' :
                sobj.props['ner'] = {'PERSON', 'ORGANIZATION'}
                sobj.props['lexname'] = {'noun.person'}
            elif word == 'what' :
                sobj.props['lexname'] = ALL_NOUNS - {'noun.person'}

        q['sobj'] = sobj
        
#Sample test
#print(question_process("Who did the Queen of England pour mustard on at dinner?"))
