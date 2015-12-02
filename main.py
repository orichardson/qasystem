#To do
# - Coreference resolution + NP datastructure
# - Maybe: full chart parse with constituents, so we can be wrong
# - WordNet: animacy
# - Get properties from:
#  * adjectives, appositives, PPs, forms of 'to be',
#      'to become', 'to turn into',  etc., i.e. identity verbs
# - Measurement Units? Make (or find) a map:
#       Adjective -> type of quanity (length, weight, etc.)
#       AND: unit --> type of quantity
#
# Preprocessing: remove commas from measurements

import sys
from magic import answerQuestions

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
