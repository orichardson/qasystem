import nltk
import os

from nltk.tag.stanford import StanfordNERTagger
st = StanfordNERTagger('stanford-ner/classifiers/english.muc.7class.distsim.crf.ser.gz', 'stanford-ner/stanford-ner.jar')

from nltk.parse import stanford
#nltk.internals.config_java(options='-xmx2G')
os.environ['STANFORD_PARSER'] = 'stanford-parser/stanford-parser.jar'
os.environ['STANFORD_MODELS'] = 'stanford-parser/stanford-parser-3.5.2-models.jar'

parser = stanford.StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")

def traverse(t, f):
    if isinstance(t, nltk.Tree) :
        # Now we know that t.node is defined
        for child in t:
            traverse(child,f)
        f(t)


def parse(string):
    split = [ s.replace('\n', ' ') for s in nltk.sent_tokenize(string)]
    rslt = parser.raw_parse_sents(split);

    trees = []

    for root in rslt:
        for tree in root:
            trees.append(nltk.ParentedTree.fromstring(tree.pformat()))

    return trees;


def maketagger(labels):
    labels.reverse()
    def nertag(node) :
        l = node.label()

        if len(node) == 1 and isinstance(node[0], str) :
            #Maybe we should check that labels.pop()[0] == node[0]
            kind = labels.pop()[1];
            if(kind != 'O') :
                node.set_label(l+'|'+kind+'')
        elif l.startswith('N') :
            # Do the last one, not the most common one. Head nouns.
            things = node[-1].label().split('|')
            if len(things) > 1:
                final = things[1]
                node.set_label(l+'|'+final+'')

    return nertag


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
