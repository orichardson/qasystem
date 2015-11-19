import nltk
import os

from nltk.tag.stanford import StanfordNERTagger
st = StanfordNERTagger('stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz', 'stanford-ner/stanford-ner.jar')

from nltk.parse import stanford
nltk.internals.config_java(options='-xmx2G')
os.environ['STANFORD_PARSER'] = 'stanford-parser/stanford-parser.jar'
os.environ['STANFORD_MODELS'] = 'stanford-parser/stanford-parser-3.5.2-models.jar'

parser = stanford.StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")

def traverse(t, f):
    try:
        t.label()
    except AttributeError:
        pass
    else:
        # Now we know that t.node is defined
        f(t)
        for child in t:
            traverse(child,f)


def parse(string):
    split = [ s.replace('\n', ' ') for s in nltk.sent_tokenize(string)]
    rslt = parser.raw_parse_sents(split);            
    return rslt;

#sentences = parser.raw_parse_sents(("Hello, My name is Melroy.", "What is your name?"))
#print(sentences);



# GUI
#for line in sentences:
 #   for sentence in line:
  #      print(sentence);