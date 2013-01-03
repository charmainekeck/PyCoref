# -*- coding: utf-8 -*-
"""
    coref.rulealgs
    ~~~~~~~~~~~~

    Algorithms for rule based for coreference resolution

    :copyright: (c) 2012 by Adam Walz, Charmaine Keck
    :license:
"""

from nltk.tree import Tree
from nltk.tokenize import word_tokenize
from Levenshtein import ratio, distance
from re import findall
from sys import maxint
import random


from data import _mk_coref_id
from helpers import vprint


def apply_rules(fileparse):
    # Phase 1 - Exact Match
    exact_match(fileparse)
    
    # Phase 2 - Precise Constructs
    precise_constructs(fileparse)
    
    # Phase 3 - Strict Head Matching
    strict_head_matching(fileparse)
    
    # Phase 4 - Strict Head Matching
    strict_head_matching(fileparse, relaxation=1)
    
    # Phase 5 - Strict Head Matching
    strict_head_matching(fileparse, relaxation=2)
    
    # Phase 6 - Relaxed Head Matching
    relaxed_head_matching(fileparse)
    
    # Phase 7 - Pronouns
    pronouns(fileparse)
    
    # Phase 8 - Very Fuzzy
    levenshtein_inclusion(fileparse)
    
    # Phase 9 - Fill `er out
    random_guessing(fileparse)


def exact_match(fileparse):
    for cid in {k: v for k,v in fileparse.nps.items() if not v.get('ref')}:
        num_found = 0
        for parse in fileparse.parses:
            num_found += parse.text.count(fileparse.nps[cid]['text'])
        if num_found > 1:
            aid = _get_cid(fileparse.nps, fileparse.nps[cid]['text'], cid)
            if not aid:
                aid = _mk_coref_id()
                data = {'text': fileparse.nps[cid]['text'], 'ref': None}
                fileparse.nps[aid] = data
            fileparse.nps[cid]['ref'] = aid


def precise_constructs(fileparse):
    # Appositive
    
    # Predicate nominative
    
    # Role appositive
    
    # Relative pronoun
    
    # Acronym
    acronym_match(fileparse)
    
    # Demonym
    
    # Number
    number_match(fileparse)


def strict_head_matching(fileparse, relaxation = 0):
    pass
    # Cluster head match
    
    # Word inclusion
    if relaxation != 2:
        word_inclusion(fileparse)

    # Compatible modifiers only
    if relaxation != 1:
        pass

    # Not i-within-i


def relaxed_head_matching(fileparse):
    pass


def pronouns(fileparse):
    for cid in {k: v for k,v in fileparse.nps.items() if not v.get('ref')}:
        proposal = hobbs(fileparse, cid)
        if proposal:
            text = ' '.join(proposal)
            aid = _get_cid(fileparse.nps, text, cid)
            if not aid:
                aid = _mk_coref_id()
                data = {'text': text, 'ref': None}
                fileparse.nps[aid] = data
            fileparse.nps[cid]['ref'] = aid


def acronym_match(fileparse):
    # Words to Acronym
    for cid in {k: v for k,v in fileparse.nps.items() if not v.get('ref')}:
        acronym = ''.join(w[0] for w in fileparse.nps[cid]['text'].split())
        num_found = 0
        for parse in fileparse.parses:
            num_found += parse.text.count(acronym)
        if num_found > 0:
            aid = _get_cid(fileparse.nps, acronym, cid)
            if aid:
                fileparse.nps[cid]['ref'] = aid

    # Acronym to words
    for cid in {k: v for k,v in fileparse.nps.items() if not v.get('ref')}:            
        if len(fileparse.nps[cid]['text'].split()) > 1:
             continue
        acronym = [r'[%s%s]' % (w.lower(), w.upper()) for w in fileparse.nps[cid]['text']]
        words_pattern = pattern = r'\w*\s'.join(acronym) + r'\w*'
        words = []
        for parse in fileparse.parses:
            words.extend(findall(words_pattern, parse.text))
        for word in words:
            aid = _get_cid(fileparse.nps, word, cid)
            if aid:
                fileparse.nps[cid]['ref'] = aid
                break


def number_match(fileparse):
    synonyms = set({u'number', u'integer', u'figure', u'digit', u'character', u'symbol',
    u'cardinal', u'ordinal', u'amount', u'quanity', u'total', u'aggregate', u'tally', u'quota',
    u'limit'})
    pattern = r'[\d\s]+'
    
    for cid in {k: v for k,v in fileparse.nps.items() if not v.get('ref')}:
        check_for_number = False
        for syn in synonyms:
            if ratio(fileparse.nps[cid]['text'].lower(), syn) > .9:
                check_for_number = True
        if not check_for_number:
            continue
 
        numbers = []
        for parse in fileparse.parses:
            numbers.extend(findall(pattern, parse.text))
        longest = ''
        if numbers:
            for num in numbers:
                if len(num) > len(longest):
                    longest = num
        if longest:
            aid = _get_cid(fileparse.nps, longest, cid)
            if not aid:
                aid = _mk_coref_id()
                data = {'text': longest, 'ref': None}
                fileparse.nps[aid] = data
            fileparse.nps[cid]['ref'] = aid


def word_inclusion(fileparse):
    for cid in {k: v for k,v in fileparse.nps.items() if not v.get('ref')}:
        if cid != '4':
            continue
        for parse in fileparse.parses:
            words = [w.lower() for w in word_tokenize(fileparse.nps[cid]['text'])]
            text = parse.text.lower()
            anaphor = ''
            num_found = 0
            majority = len(words) / 2
            for word in words:
                if text.find(word + ' ') != -1:
                    num_found += 1
            if num_found >= majority:
                first_index = len(text)
                last_index = 0
                for word in words:
                    if text.find(word + ' ') != -1 and text.find(word + ' ') < first_index:
                        first_index = text.find(word)
                    if text.find(word) != -1 and text.find(word ) + len(word) > last_index:
                        last_index = text.find(word) + len(word)
                if first_index < last_index:
                    anaphor = text[first_index:last_index]
            if anaphor:
                aid = _get_cid(fileparse.nps, anaphor, cid)
                if not aid:
                    aid = _mk_coref_id()
                    data = {'text': anaphor, 'ref': None}
                    fileparse.nps[aid] = data
                fileparse.nps[cid]['ref'] = aid
                break


def levenshtein_inclusion(fileparse):
    for cid in {k: v for k,v in fileparse.nps.items() if not v.get('ref')}:
        referent = fileparse.nps[cid]['text'].lower()
        
        # Search Tagged corefs
        for aid in fileparse.nps:
            anaphor = fileparse.nps[aid]['text'].lower()
            cRatio = 0.6
            temp_ratio = ratio(referent, anaphor)
            if temp_ratio > cRatio:
                cRatio = temp_ratio
                fileparse.nps[cid]['ref'] = aid
        
        
        for parse in fileparse.parses:
            text = parse.text.lower()
            dist = maxint
            proposal = ''
            while len(text) > 2:
                if distance(text, referent) < dist:
                    dist = distance(text, referent)
                    proposal = text
                text = text[1:]
                if distance(text, referent) < dist:
                    dist = distance(text, referent)
                    proposal = text
                text = text[:-1]
                if distance(text, referent) < dist:
                    dist = distance(text, referent)
                    proposal = text
            if ratio(text, referent) > 0.3:
                aid = _get_cid(fileparse.nps, fileparse.nps[cid]['text'], cid)
                if not aid:
                    aid = _mk_coref_id()
                    data = {'text': fileparse.nps[cid]['text'], 'ref': None}
                    fileparse.nps[aid] = data
                fileparse.nps[cid]['ref'] = aid


def random_guessing(fileparse):
    prevs = []
    num = 0
    sort_key = lambda x:int(x[0]) if x[0].isdigit() else (float('inf'),x[0])
    corefs = sorted(fileparse.nps.items(), key = sort_key)
    
    for cid in [k for k,v in corefs if not v.get('ref')]:
        if len(prevs) > num and cid.isdigit():
            choice = min(len(prevs), int(round(random.weibullvariate(1.2,7))) + 1)
            fileparse.nps[cid]['ref'] = prevs[-choice]
        if cid.isdigit():
            prevs.append(cid)


def hobbs(fileparse, coref_id, hobbs_type='pronoun'):
    # Begin at NP immediately dominating the pronound
    pid, pos, tree = _get_dominating_np(fileparse, coref_id)

    # only use hobbs on pronouns
    if  pid is None or not pos:
        return None
    correct_type, matcher = _hobbs_rules(hobbs_type, pid, pos, fileparse)

    if not correct_type(pos):
        return None

    # Go up tree to first NP or S.
    pos, path = _go_up_to_S_or_NP(tree, pos)

    # Traverse all branches below pos to the left of path.
    proposal = _traverse(tree, pos, path, None, matcher)

    while not proposal:
        # If pos is the highest S in the sentence,
        if pos == (0,):
            # traverse the parse trees of the previous sentences
            # in the order of recency.
            if pid == 0:
                return None
            pid -= 1
            tree = fileparse.parses[pid].ptree

            # Traverse left-to-right, breadth first.
            # When a NP is encountered, propose as antecedent.
            proposal = _traverse(tree, (), [], proposal, matcher)

        else:
            # From node pos, go up the tree to the first NP or S.
            pos, path = _go_up_to_S_or_NP(tree, pos)

        # If pos is an NP and the path to pos did not pass through the nominal
        # that pos immediately dominates, propose pos as antecedent
        if tree[pos].node == 'NP':
            proposal = _propose_if_new(tree, pos, path, proposal, matcher)

        # Traverse all branches below pos to the left of the path
        # Propose any NP encountered as the antecdent
        proposal = _traverse(tree, pos, path, proposal, matcher)

        # If pos is an S node, traverse to the right of path, but do not go
        # below any NP or S node.
        # Propose any NP node as antecedent
        if tree[pos].node == 'S':
            proposal = _traverse(tree, pos, path, proposal, matcher,
                                       direction='r')

    return tree[proposal].leaves()


def _get_dominating_np(fileparse, coref_id):
    for i in range(len(fileparse.parses)):
        tree = fileparse.parses[i].ptree
        for p in tree.treepositions():
            try:
                if tree[p].node == 'COREF_TAG_%s' % coref_id:
                    return i, p, tree
            except AttributeError:
                continue
    return None, None, None


def _traverse(tree, pos, path, proposal, matcher, direction='l'):
    # bounds checks if position is left of the path (path implies 2 nodes)
    if direction == 'left':
        bounds = lambda p: len(path) < 2 or p < path[-2]
    else:
        bounds = lambda p: len(path) < 2 or p > path[-2]

    for sub_pos in tree[pos].treepositions():
        p = pos + sub_pos
        if isinstance(tree[p], Tree) and bounds(p) and p not in path:
            if direction == 'r':
                if tree[p].node == 'NP' or tree[p].node == 'S':
                    break

            # Propose any NP that has a NP or S between it and pos
            if tree[p].node == 'NP' and matcher(tree[p]):
                proposal = p
    return proposal


def _go_up_to_S_or_NP(tree, pos):
    path = [pos]
    while True:
        pos = pos[:-1]
        path.append(pos)
        if tree[pos].node == 'S' or tree[pos].node == 'NP':
            break
    return pos, path


def _propose_if_new(tree, pos, path, proposal, matcher):
    for i in range(len(tree[pos])):
        temp_pos = pos + (i,)
        if tree[temp_pos].node.startswith('N') and temp_pos in path:
            if matcher(tree[pos]):
                proposal = temp_pos
    return proposal


def _hobbs_rules(hobbs_type, pid, pos, fileparse):
    tree = fileparse.parses[pid].ptree
    if hobbs_type == 'pronoun':
        correct_type = lambda pos: (len(tree[pos]) == 1 and
                                    tree[pos].pprint().find('PRP') != -1)
        matcher = _hobbs_pronoun_match(tree[pos], pid, fileparse)
    elif hobbs_type == 'exact':
        correct_type = lambda pos: True
        
        matcher = _hobbs_exact_match(tree[pos])
    else:
        correct_type, matcher = False, None

    return correct_type, matcher


def _hobbs_pronoun_match(referant, pid, fileparse):
    word = set([w.lower() for w in referant.leaves()])
    words = fileparse.parses[pid].words
    
    number = {'singular': set({'i', 'me', 'my', 'mine', 'myself',
                               'you', 'your', 'yours', 'yourself',
                               'he', 'him', 'his', 'himself',
                               'she', 'her', 'hers', 'herself',
                               'it', 'its', 'itself'}),
              'plural': set({'we', 'us', 'our', 'ours', 'ourselves',
                               'you', 'your', 'yours', 'yourselves',
                               'they', 'them', 'their', 'theirs', 'themselves'})
             }
    gender = {'masculine': set({'he', 'him', 'his', 'himself'}),
              'feminine': set({'she', 'her', 'hers', 'herself'}),
              'neuter': set({'it', 'its', 'itself'})}
    person = {'first': set({'I', 'me', 'my', 'mine', 'myself',
                            'we', 'us', 'our', 'ours', 'ourselves'}),
              'second': set({'you', 'your', 'yours', 'yourself','yourselves'}),
              'third': set({'he', 'him', 'his', 'himself',
                            'she', 'her', 'hers', 'herself',
                            'it', 'its', 'itself',
                            'they', 'them', 'their', 'theirs', 'themselves'})}
    animate = set({'I', 'me', 'my', 'mine', 'myself',
                   'you', 'your', 'yours', 'yourself',
                   'he', 'him', 'his', 'himself',
                   'she', 'her', 'hers', 'herself',
                   'we', 'us', 'our', 'ours', 'ourselves',
                   'you', 'your', 'yours', 'yourselves',
                   'they', 'them', 'their', 'theirs', 'themselves'})

    def matcher(proposal):
        pword = set([w.lower() for w in proposal.leaves()])

        matches_number = False
        if (word & number['singular']):
            parts = set({'NN', 'PP'})
            for sub in proposal.subtrees():
                if sub.node in parts or (pword & number['singular']):
                    matches_number = True
        elif (word & number['plural']):
            parts = set({'NNS', 'NPS', 'NN'})
            for sub in proposal.subtrees():
                if sub.node in parts or (pword & number['plural']):
                    matches_number = True

        matches_gender = False
        if word in gender['masculine']:
            pass
        elif word in gender['feminine']:
            pass
        elif word in gender['neuter']:
            matches_gender = True
        
        #TODO: Match person
        matches_person = True

        #return matches_number and matches_gender and matches_person 
        return True
    return matcher


def _hobbs_exact_match(referent):
    referent = ' '.join([s.lower().strip() for s in referent.leaves()])
    
    def matcher(proposal):
        proposal = ' '.join([s.lower().strip() for s in proposal.leaves()])
        return referent == proposal
    
    return matcher
    
def _get_cid(nps, np, referent_id):
    if not np:
        return None
    normalized_anaphor = ' '.join(np.split()).lower()
    
    sort_key = lambda x:int(x[0]) if x[0].isdigit() else (float('inf'),x[0])
    for cid, coref in  sorted(nps.items(), key=sort_key):
        normalized_coref = ' '.join(coref['text'].split()).lower()
        if normalized_coref == normalized_anaphor and cid != referent_id:
            return cid
    return None


def _sort_data(fileparse):
    sorted_data = {}
    for prior_reference in fileparse.words:
        for pair in prior_reference:
            referer = pair[0][0]
            referent = pair[1][0]
            
            sorted_data[(pair[0][1],pair[0][3],pair[0][4])] = (referer, referent)
    return sorted(sorted_data.values(), key=lambda x: (x[0], x[1]))
            
