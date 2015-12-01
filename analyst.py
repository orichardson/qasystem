"""
@author: Oliver
"""

from libutils import *
import lawyer


class Story:
    # obj[]: list of objects

    def __init__(self):
        self.obj = []
        self.verbs = [] # Keep a list of verbs and their senses,
            # with which to compare similarity

class SObj:
    # TODO: train perceptron on these.
    WORTH = lawyer.faireValoir()
    SINGULAR_POS = ['NNP', 'NN', 'DT', 'VBZ']
    PLURAL_POS = ['NNS', 'NNPS', 'CD', 'VBP' ]

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
            self.props['ner'] = self.nertag
        # Step (2) : Verbs:
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
                    #self.props['number'] -= {'s'}
                    pass
                    # Technically, it could be non-3rd person as well, but
                    # news articles are very 3rd person-y.

        # Step (4) : parse agreement
        nsing = len([x[0] for x in node.pos() if x[1] in SObj.SINGULAR_POS])
        npl = len([x[0] for x in node.pos() if x[1] in SObj.PLURAL_POS])

        if(nsing + npl > len(leaves)/3) :
            if nsing > npl :
                self.props['number'] = {'s'}
            else :
                self.props['number'] = {'p'}


    def attrcollector(node) : # another traversal function, collects PPs and JJ's
        pass

    def compatibility(self, other): # Could these two nodes co-refer?
        score = 0

        joint = self.props.keys() & other.props.keys()

        for prop in joint:
            intersect = len(self.props[prop] & other.props[prop])
            union = len(self.props[prop] | other.props[prop])

            # Jaccard similarity!
            if intersect:
                score += SObj.WORTH[prop] * (intersect/union)
            else :
                score -= SObj.WORTH[prop] * StoryBuilder.PENALTY_MULTIPLIER

        #score /= len(joint)

        maxv = 0
        for t1 in self.texts:
            for t2 in other.texts:
                v = lexsim(t1,t2)
                if(v > maxv):
                    maxv = v

        nproper = 0;

        for t in self.trees+other.trees:
            count = len(list(t.subtrees(filter=lambda n: n.label() in ['NNP', 'NNPS'])))
            nproper += count / len(list(t.subtrees()))

        score += maxv*SObj.WORTH['lexsim']*nproper

        # Now scale by total semantic distance
        score /= 1+semanticDist(self.texts, other.texts)
        #print(self.texts[0], other.texts[0], score, sep='\t')

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

class Pronoun(SObj):
    def __init__(self, stry, node):
        super(Pronoun, self).__init__(stry, node)
        content = node[0].lower()
        label = node.label()
        if content == 'he' or content == 'him':
            self.props['person'] = {'3'}
            self.props['number'] = {'s'}
            self.props['gender'] = {'m'}
            self.props['lexname'] = {'noun.person'}
        elif content == 'she' or content == 'her':
            self.props['person'] = {'3'}
            self.props['number'] = {'s'}
            self.props['gender'] = {'f'}
            self.props['lexname'] = {'noun.person'}
        elif content == 'they' or content == 'them':
            self.props['person'] = {'3'}
            self.props['number'] = {'p'}
            self.props['lexname'] = {'noun.group'}



class StoryBuilder:
    MERGE_THRESHOLD = 6
    CGRAMMAR = lawyer.get('patterns')
    PENALTY_MULTIPLIER = 10

    def __init__(self, story=Story()):
        self.story = story


    def resolve(self, given):
        # pronouns: he/she,you--> lexname() = noun.person, number = {1}, gender=m/f
        #   they --> lexname() = group,

        maxo = None
        maxsim = 0

        for o in self.story.obj:
            v = o.compatibility(given)
            if v > maxsim:
                maxo = o
                maxsim = v

        if maxsim > StoryBuilder.MERGE_THRESHOLD:
            print('merging because of score : ', maxsim, maxo.texts, maxo.props, given.texts, given.props,sep='\n')
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
                # Need to check how necessary this is to resolve:
                # High priority: her, hers, she, he,
                # medium priority: It (could be pleonastic) -- 'the dog', etc
                # low priority: general NP

                # First, check for apositive construction;
                # otherwise, if this is a lowest level NP, resolveee.
                m = getMatches(StoryBuilder.CGRAMMAR, node)
                
                # Check that this is not a list
                if 'APPOSITIVE' in m :
                    # because it's a postorder traversal, our children already
                    # live in the story obj list...
                    print('merging because appositive')
                    node[0].obj.merge(node[2].obj)

                if len(list(node.subtrees(filter=lambda x: x.label()=='NP') )) == 1 :
                    thing = self.resolve(SObj(self.story, node))
                for i in node.subtrees(filter=lambda x: x.label() == 'PRP'):
                    thing = self.resolve(Pronoun(self.story, i))

        return reader

#Next most important thing is the semantic distance
