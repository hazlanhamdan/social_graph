'''
graph_analyze.py

Script for constructing and analyzing a social graph based on names of 
people who appear together in photos.  Part of the first project for 
The Data Incubator.  

Author: Phillip Schafer (phillip.baker.schafer@mg.thedataincubator.com)
Date: April 11, 2015

Usage:
>> python graph_scrape.py
'''
import pickle
import re
import string
import networkx as nx
import operator
import pickle

def extract_names(caption):
    '''
    Extract a list of names from a caption string.  
    Names should be in format 'Firstname Lastname'.  
    If no names extracted, return None.  

    This function splits up the string using 'when', 'and', and commas
    and passes the resulting segments to the function `parse_names`
    '''
    # Remove leading and trailing whitespace
    match = re.search('^\s*([^\s].+[^\s])\s*$', caption, re.DOTALL)
    if match:
        caption = match.group(1)
    else: 
        print caption
        print 'NO CHARACTERS FOUND'
        return None
    
    # If too long, throw out the caption
    if len(caption) > 250:
        print 'TOO LONG'
        return None
        
    # initialize the list
    names = []
    
    # split on pattern '... with ...'
    # if there's a match, parse the segment before the 'with',
    # leave the rest to be split below
    segments = re.split('\swith\s', caption)
    if len(segments)==2:
        new_names = parse_names(segments.pop(0))
        if new_names:
            for nm in new_names:
                if nm != None: names.append(nm)
    elif len(segments)>2:
        print '***** UNHANDLED CASE: MORE THAN 1 "WITH" *****'
        print caption
        return None
    # after this, segments have length 1
        
    # split on the pattern 'name, name, and name'
    segments = re.split('\s?,\s?(?:and)?\s?', segments[0])
        
    # if not split already, split on pattern 'name and name',
    # but ONLY IF it's not a 'jack and jane doe' case
    if len(segments)==1:
        test_segs = re.split('\sand\s', segments[0])
        # 'jack and jane doe' case indicated by no whitespace in 
        # the first test_seg
        if re.search('\s', test_segs[0]):
            segments = test_segs
    
    #parse all the segments
    for sg in segments:
        new_names = parse_names(sg)
        if new_names:
            for nm in new_names:
                if nm != None: names.append(nm)
    
    return names

def parse_names(seg):
    '''
    Parse the names in segments generated in `extract_names`.
    If parsing fails, return None.

    Except for a few special cases, each segment is assumed to contain
    only one name. 
    '''
    # remove text in parentheses
    seg = re.sub(r'^\([^\)]*\)\s', '', seg) # bol
    seg = re.sub(r'\s\([^\)]*\)\.?$', '', seg) # eol
    seg = re.sub(r'\s\([^\)]*\)\s', ' ', seg) # elsewhere
    
    # All subsequent processing is word by word....
    words = string.split(seg)
    
    titles = ('Dr.', 'Mayor', 'Mr.', 'Mrs.', 'Ms.', 'Sir', 'Justice', 'Governor'
              'Prince', 'Princess', 'King', 'Queen', 'Count', 'Countess', 'Baroness')
    
    flags = ('Honoree','Chair','Co-Chair','Trustee','Director','Chairman','Designer','Administrator','Winner','Fellow',
             'Actress','Playwright','Curator','Laureate','Member','Governor','Representative','Host','Vice-Chair',
             'Rev.','Reverend','Conductor','Mayor','Co-Chairs','Lady','Designer/artist','President','Recipient','Editor',
             'Commissioner','General','Speaker','Teacher','Sgt.')
    if len(words)>2 and (words[-3] in flags or re.search(r':$', words[-3]) or re.search(r"'s", words[-3])):
      words = words[-2:]
    elif len(words)>3 and (words[-4] in flags or re.search(r':$', words[-4]) or re.search(r"'s", words[-4])):
      words = words[-3:]
    
    # Special case: '[Tt]he Honorable'
    if len(words)==4 and (words[0]=='the' or words[0]=='The') and words[1]=='Honorable':
        return [' '.join([words[2], words[3]])]
    
    # Special case: 'jack and jane doe'
    if len(words)==4 and words[1]=='and':
        if not all(check_caps(wd) for wd in [words[0],words[2],words[3]]):
            return None
        return [' '.join([words[0], words[3]]), ' '.join([words[2], words[3]])]
    
    # Special case: 'mr. and mrs. jane doe'
    if len(words)==5 and words[0] in titles and words[2] in titles and words[1]=='and':
        if not all(check_caps(wd) for wd in words[3:]):
            return None
        return [' '.join([words[3], words[4]])]
    
    # If not capitalized like a name, throw out
    if not all(check_caps(wd) for wd in words):
        return [None]
    
    if len(words)==1:
        return [None]
    elif len(words)==2:
        return [' '.join(words)]
    elif len(words)==3:
        if words[0] in titles:
            return [' '.join(words[1:])]
        else:
            return [' '.join([words[0], words[2]])]
    elif len(words)==4 and words[0] in titles:
        return [' '.join([words[1], words[3]])]
    else:
        print
        print '***** UNHANDLED CASE: SEGMENT PATTERN UNMATCHED *****'
        print
        #print seg
        return [None]

def check_caps(word):
    '''
    Return a boolean indicating whether a putative word in a name follows 
    the right capitalization conventions

    We require that the first alphanumeric character be uppercase (leading
    quotations and other punctuation are allowed) and that it is followed 
    by at least one lowercase character.  
    '''
    # get the first letter, False if none found
    match = re.search('\w', word)
    if not match: 
        return False
    first_let = match.group()
    # First letter must be uppercase
    if not first_let.isupper():
        return False
    # There must be at least one lowercase letter
    match = re.search('[a-z]', word)
    if not match: 
      return False
    return True

def make_graph(captions):
    ''' 
    Construct a graph using the captions
    '''
    g = nx.Graph()
    for cp in captions:
        names = extract_names(cp)
        if names:
            add_names(names, g)
    return g

def add_names(names, g):
    '''
    Add names to a graph - helper function for `make_graph`
    '''
    # loop thru all pairs of names (but not self-pairs)
    for n1 in names:
        for n2 in names:
            if n1==n2: continue
            if g.has_edge(n1,n2):
                g[n1][n2]['weight'] += 0.5
            else:
                g.add_edge(n1, n2, weight=0.5)

def test_captions(captions):
    '''
    For debugging the caption parsing
    '''
    for cp in captions[145:201]:
        print cp
        names = extract_names(cp)
        if names:
            for nm in names: print nm
        print

def view_graph(g, N):
    '''
    For debugging the graph construction
    '''
    print g.nodes()[:N]
    print
    print g.edges(data=True)[:N]
    print

  
# return top 100 tuples (name, degree)
def q1(g):
    def getKey(item):
        return item[1]
    degs = [(node, degree) for node, degree in g.degree_iter()]
    ans = sorted(degs, key=getKey, reverse=True)[:100]
    pickle.dump(ans, open('q1.p', 'wb')) 
  
    print 'DEGREE:\n'
    print ans
    print
  
# return top 100 tuples (name, pagerank)
def q2(g):
    rank = nx.pagerank(g)
    ans = sorted(rank.items(), key=operator.itemgetter(1), reverse=True)[:100]
    pickle.dump(ans, open('q2.p', 'wb')) 

    print 'PAGERANK:\n'
    print ans
    print

# return list of top 100 edges (name, name, weight) ordered by weight
def q3(g):
    def getKey(item):
        return item[1]
    edg = [((node1, node2), int(data['weight'])) for node1, node2, data in g.edges_iter(data=True)] 
    ans = sorted(edg, key=getKey, reverse=True)[:100]
    pickle.dump(ans, open('q3.p', 'wb')) 

    print 'BEST FRIENDS:\n'
    print ans
    print


def main():
    # Load the list of unicode caption strings
    captions = pickle.load(open('captions.p', 'rb'))
    #test_captions(captions)

    g = make_graph(captions)
    #view_graph(g, 25)

    q1(g)
    q2(g)
    q3(g)

if __name__ == '__main__':
    main()