"""
@author: Oliver
"""

from nltk.corpus import wordnet as wn
from nltk.wsd import lesk
from libutils import *
import lawyer
 
def lexclass(word, context=''):
    # TODO: word sense disambiguation, pass optional context to lexclass.
    rslt = set()
    
    if context:
        sense = lesk(context,word);
        if sense:
            rslt.add(sense.lexname())
            return rslt
    
    sets = wn.synsets(word, pos=wn.NOUN)
    for s in sets:
        rslt.add(s.lexname())
            
    return rslt


class Story:
    # obj[]: list of objects

    def __init__(self):
        self.obj = []
        self.verbs = [] # Keep a list of verbs and their senses, 
            # with which to compare similarity 
        
class SObj:
    # TODO: train perceptron on these.
    WORTH = lawyer.faireValoir()
    
    
    def __init__(self, stry, node):
        self.story = stry        
        
        #Two-way reference, just to be safe.        
        node.obj = self
        self.trees = [node] # ... but multiple NP's can have the same SObj

        leaves = node.leaves()
        self.texts = [' '.join(leaves)]
        
        self.props = {}
        
        #This is sketchy, maybe. Should we look for context in the paragraph instead?        
        context = ' '.join(node.root().leaves())
        lname = lexclass(leaves[-1], context)
        self.props['lexname'] = lname
        
        # Initially, every person/number is possible. Eliminate these when 
        # verbs don't agree, semantic classes don't agree, or NER forces one.
        
        # Step (1) : Semantic class agreement
        lawyer.addConstraints('lexname_constraints', self.props, lname ,'U')     
        # Step (2) : NER agreement:
        if hasattr(self,'nertag') :
            lawyer.addConstraints('ner_constraints', self.props, self.nertag)

        # Step (3) : Verbs: 
        # Note that, unlike nouns, where the head noun is at the end,
        # the conjugated verb always comes first in a verb phrase.
        nextpart = node.right_sibling()
        if nextpart and nextpart.label() == 'VP' :
            vpos = findLeftNode(nextpart).label()
            
            if(vpos == 'VBZ'):
                self.props['person'] = {'3'}
                self.props['number'] = {'s'}
            
            elif(vpos == 'VBP') :
                if 'number' in self.props:
                    self.props['number'] -= {'s'}
                    # Technically, it could be non-3rd person as well, but
                    # news articles are very 3rd person-y.

        
    def attrcollector(node) : # another traversal function, collects PPs and JJ's
        pass       
        
    def compatibility(self, other): # Could these two nodes co-refer?
        score = 0
        
        for prop in self.props.keys() & other.props.keys():
            if self.props[prop] & other.props[prop]:
                score += SObj.WORTH[prop]
            else :
                score -= SObj.WORTH[prop]
        
        maxv = 0
        for t1 in self.texts:
            for t2 in other.texts:
                v = lexsim(t1,t2)
                if(v > maxv):
                    maxv = v
        
        score += maxv*SObj.WORTH['lexsim']
        
        #print(self.texts[0]+",\t,"+other.texts[0])
        #print(score)
        
        return score
        
    def merge(self, other) :
        for t in other.trees:
            t.obj = self;
            
        self.trees.extend(other.trees)
        self.texts.extend(other.texts)
        
        for po in other.props.keys():
            if po in self.props:
                self.props[po] &= other.props[po]
            else:
                self.props[po] = other.props[po]
        
        if(other in other.story.obj) :
            other.story.obj.remove(other)               
        
        
        

class StoryBuilder:
    MERGE_THRESHOLD = 0.5    
    
    def __init__(self, story=Story()):
        self.story = story
      
    
    def resolve(self, given):
        # pronouns: he/she,you--> lexname() = noun.person, number = {1}, gender=m/f
        #   they --> lexname() = group,
    
        # TODO: Never merger vertically. 
        maxo = None
        maxsim = 0
        
        for o in self.story.obj:
            v = o.compatibility(given)
            if v > maxsim:
                maxo = o
                maxsim = v
        
        if maxsim > StoryBuilder.MERGE_THRESHOLD:
            maxo.merge(given)
            return maxo
        else:
            self.story.obj.append(given)            
            return given
        
        
    # call this with each tree, to build a story structure
    def read(self, trees) :
        r = self.makeReader()
        for tree in trees :
            traverse(tree,r)
            
        
    def makeReader(self):
        def reader(node):
            tag = node.label();
            if(tag == 'NP'):
                thing = self.resolve(SObj(self.story, node))
                self.story.obj.append(thing)
            elif(tag == 'PRP'):
                #thing = self.resolve()
                pass
            
        return reader
            
            
