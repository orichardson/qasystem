# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 01:31:34 2015

@author: Oliver
"""

def get(filename, unpack=False):
    ruleFile = open('./rules/'+filename+'.txt', 'r')
    rslt = {}
    
    for line in ruleFile :
        if not len(line) or line[0] == '#':
            continue
        
        parts = line.replace('\n','').split('\t')
        
        # Next line is jut a complicated way of taking out tildae, which indicate
        # a lack of property
        if(unpack):
            rslt[parts[0]] = float(parts[1])
        else:
            rslt[parts[0]] = [('' if x == '~' else x) for x in parts[1:]] 
        
    return rslt
    
def setMerge(a, b, op):
    if op == 'U':
        return set(a) | set(b)
    return set(a) & set(b)

"""
Mode can be either 'U', for union, or 'I', for intersection
"""
def addConstraints(filename, obj, prop, mode='I'):
    constr = get(filename)     
    for (i,l) in enumerate(constr['VALUES']) :
        for v in prop & constr.keys():
            mine = constr[v][i]
            theirs = obj[l] if l in obj else mine
        
            obj[l] = setMerge(mine,theirs,mode)        
        
def faireValoir():
    return get('property_weights', unpack=True);