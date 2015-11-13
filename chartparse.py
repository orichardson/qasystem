import heapq

def parse(words, grammar):
    agenda = []
    chart = []

    for (i,w) in enumerate(words):
        heapq.heappush(agenda, (5, w, i, i+1))

    while(agenda):
        x = heapq.heappop(agenda);
        print(x);
        
        chart.append(x[1:])
        
    return chart;

print('hi')
parse('this is a sentence'.split(' '));
