#import nltk

from question_process import question_process
from libutils import *;

#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')

def makeScorer(q) :
    q['bestscore'] = -1;
    q['bestans'] = 'No Answer'
    
    def scorer(node):
        nodetext = node.label().strip();
        score = 0;

        print(q['searchtype'] + '\t'+ nodetext+'\t'+str(q['searchtype']==nodetext));  
        
        if 'searchtype' in q and (nodetext == q['searchtype']) :
            score += 10;
        
        for constr in q['constraints'] :
            pass
            #if( node has property constr[0]) :
                #dscore += constr[1] 
                            
        #Check sores here.            
        if(score > q['bestscore']) :
            q['bestscore'] = score
            q['bestans'] = ' '.join(node.leaves())
    
    return scorer

def answerQuestions(story, questions):
    trees = list(parse(story))
    
    for q in questions: 
        scorer = makeScorer(q);
        question_process(q);
        
        print(type(trees))
        
        for root in trees:
            for tree in root:
                print('TREE')
                #tree.draw();
                traverse(tree, scorer)
                
        q['Answer'] = q['bestans'];

        
    print('all done!')

