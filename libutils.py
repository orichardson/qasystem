import nltk, os, math

from nltk.tag.stanford import StanfordNERTagger
st = StanfordNERTagger('stanford-ner/classifiers/english.muc.7class.distsim.crf.ser.gz', 'stanford-ner/stanford-ner.jar')

from nltk.parse import stanford

#nltk.internals.config_java(options='-xmx2G')
os.environ['STANFORD_PARSER'] = 'stanford-parser/stanford-parser.jar'
os.environ['STANFORD_MODELS'] = 'stanford-parser/stanford-parser-3.5.2-models.jar'

parser = stanford.StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")

from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
from nltk.wsd import lesk

wnl = WordNetLemmatizer()

def isplural(word):
    lemma = wnl.lemmatize(word, 'n')
    plural = True if word is not lemma else False
    return plural, lemma


def lexsense(word, context='') :
    if context:
        sense = lesk(context,word);
        if sense:
            return {sense}

    return set(wn.synsets(word, pos=wn.NOUN))

def lexclass(word, context=''):
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

def bagSimilarity(s1, s2) :
    if(len(s1) == 0 and len(s2) == 0) :
        return 1
        
    total = 0;

    for a in s1:
        for b in s2:
            total += wn.lch_similarity(a,b)

    total /= (len(s1)*len(s2))
    return total


def semSim(texts1, texts2):
    s1 = set()
    s2 = set()

    for t in texts1:
        for q in t.split():
            s1 |= lexsense(q, t)
    for t in texts2:
        for q in t.split():
            s2 |= lexsense(q, t)

    return bagSimilarity(s1, s2)


def traverse(t, f, pre=False):
    if isinstance(t, nltk.Tree) :
        # Now we know that t.node is defined
        if pre:
            f(t)

        for child in t:
            traverse(child,f)

        if not pre:
            f(t)

def findLeftNode(t) :
    if isinstance(t, nltk.Tree):
        if len(t) :
            n = findLeftNode(t[0])
            return n if n else t
        return t
    return None

def ismatch(ltags, node) :
    return ' '.join(ltags) is ' '.join([x.label()  for x in node if isinstance(x,nltk.Tree)])

def getMatches(grammar, node):
    matches = set()

    for g in grammar.keys():
        # risky business here: use in, or is? Do we need exact match?
        if ismatch(grammar[g], node) :
            matches.add(g)

    return matches



def parse(string):
    split = [ s.replace('\n', ' ') for s in nltk.sent_tokenize(string)]
    rslt = parser.raw_parse_sents(split);

    trees = []

    for root in rslt:
        for tree in root:
            #trees.append(tree)
            trees.append(nltk.ParentedTree.fromstring(tree.pformat()))

    return trees;



def maketagger(labels):
    labels.reverse()

    def nertagger(node) :
        l = node.label()

        if len(node) == 1 and isinstance(node[0], str) :
            # We are now checking that labels.pop()[0] == node[0]
            newlabel = labels.pop();

            if(l == newlabel[0]) :
                node.nertag = newlabel[1];

        elif l.startswith('N') :
            # Do the last one, not the most common one. Head nouns.
            node.nertag = getattr(node[-1], 'nertag', 'O')

    return nertagger

"""
This method was taken almost entirely from a wikipedia page with edit
distance code in many different languages
"""
def levenshtein(s1, s2) :
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

"""
... and this is why we need it.
Returns lexical similarity between two strings (0-1)
Edit distance + Acronyms + other ways of co-referring to strings
where semantics and syntax don't help at all (using just first names, etc.)
"""

def acronimify(s):
    s.replace('.', '')
    s.replace('of', '')
    s.replace('and', '')
    s.split()
    s = [i[0].lower() for i in s]

def isacronym(s1, s2):
    s1.replace('.', '')


def lexsim(s1, s2):
    dist = levenshtein(s1,s2)


    #Now do fancy acronym and missing word / reordering things to add score.
    amelioration = 2 # should be greater for reorderings, less for egregious mistakes

    '''if isacronym(s1,s2):
        amelioration = 1000
    if issubphrase(s1,s2):
        amelioration = 100'''

    # and now to clamp it to the appropriate range:
    return 1/(1 + dist/amelioration)




#trees = []
#for i in parse('I am a sentence at Apple, Co.'):
#    for j in i:
#        print(type(j.leaves()[0]))
#        print(st.tag(j.leaves()))

#print(st.tag('I am a sentence at Apple , Co.'.split(' ')))
#sentences = parser.raw_parse_sents(("Hello, My name is Melroy.", "What is your name?"))
#print(sentences);



# GUI
#for line in sentences:
 #   for sentence in line:
  #      print(sentence);
