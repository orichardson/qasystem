#To do
# - Coreference resolution + NP datastructure
# - WordNet: animacy
# - Get properties from adjectives, appositives, PPs

import sys
from magic import answerQuestions
import nltk

#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')

inputFileN = sys.argv[1]
#inputFileN = 'test_input'

inputFile = open(inputFileN, 'r')

directory = inputFile.readline().replace('\n', '')

for storyID in inputFile:
    storyID = storyID.replace('\n', '')
    storyFile = open(directory+'/'+storyID+'.story', 'r')
    qFile = open(directory+'/'+storyID+'.questions', 'r')

    for line in storyFile:
        if line.startswith('TEXT:'):
            break

    storyText = storyFile.read()

    # Go through each quetion, and extract the question text.

    questions = []

    currentQ = {}
    for line in qFile:
        pieces = [i.strip() for i in line.split(':') ]

        if len(pieces) == 2 and not (pieces[0] in currentQ) :
            currentQ[pieces[0]] = pieces[1]
        else:
            questions.append(currentQ)
            currentQ = {}
            continue

    #########################
    ###   DO magic here   ###
    #########################
    answerQuestions(storyText, questions)

    THINGSTOPRINT = ['QuestionID', 'Question', 'Answer']

    for q in questions:
        for attr in THINGSTOPRINT:
            if attr in q:
                print(attr+': '+q[attr])
        print()
