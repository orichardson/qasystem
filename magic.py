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
        nodetext = node.label().strip();
        score = 0;

        leaves = node.leaves();

        #print(q['searchtype'] + '\t'+ nodetext+'\t'+str(q['searchtype']==nodetext));

        if 'searchtype' in q and (nodedata[0] ==q['searchtype']) :
            score += 10 ;

        for constr in q['constraints'] :
            pass
            #if( node has property constr[0]) :
                #dscore += constr[1]

        # Now, do general statistical weighting based on words
        words = node.root().leaves();
        common =  len([val for val in  q['assoc_verbs'] if val[0] in words])
        common +=  len([val for val in  q['assoc_nouns'] if val[0] in words])

        #print(words)
        #print([val for val in  q['assoc_nouns'] if val[0] in words])
        #print([val for val in  q['assoc_verbs'] if val[0] in words])

        score += 15*common;

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
        print(tree)

    for q in questions:
        scorer = makeScorer(q);
        question_process(q);
        
        global stry
        stry = analyst.Story()
        sb = analyst.StoryBuilder(stry)
        sb.read(trees)

        for tree in trees:
            traverse(tree, scorer)

        q['Answer'] = q['bestans'];


    #print('all done!')
