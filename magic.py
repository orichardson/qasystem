#import nltk

from question_process import question_process
from libutils import *;
import analyst

#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')

def makeScorer(q) :
    q['bestscore'] = -1;
    q['bestans'] = 'No Answer'

    def scorer(node):
        score = 0;
        #print(q['searchtype'] + '\t'+ nodetext+'\t'+str(q['searchtype']==nodetext));

        if 'searchtype' in q and (node.label() ==q['searchtype']) :
            score += 20 ;
            
        if hasattr(node, 'obj') and 'sobj' in q:
            score += 5*node.obj.compatibility(q['sobj'])
            
        leaves = node.leaves()

        score /= (20 + len(leaves))
        score /= (10 + len(node.treeposition()))

        #print(str(common)+'\t'+str(score)+'\t'+' '.join(leaves))

        #Check sores here.
        if(score > q['bestscore']) :
            q['bestscore'] = score
            q['bestans'] = ' '.join(leaves)

    return scorer

def answerQuestions(story, questions):
    trees = parse(story)

    for tree in trees:
        labels = st.tag(tree.leaves())
        tagger = maketagger(labels)
        traverse(tree, tagger)

    for q in questions:
        scorer = makeScorer(q);
        question_process(q);

        sb = analyst.StoryBuilder()
        sb.read(trees)
        
        for tree in trees:
            traverse(tree, scorer)

        q['Answer'] = q['bestans'];