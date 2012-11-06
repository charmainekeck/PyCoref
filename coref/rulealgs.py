# -*- coding: utf-8 -*-
"""
    coref.rulealgs
    ~~~~~~~~~~~~

    Algorithms for rule based for coreference resolution

    :copyright: (c) 2012 by Adam Walz, Charmaine Keck
    :license:
"""

from nltk.tree import Tree
import random

from data import _mk_coref_id
from helpers import vprint


def apply_rules(fileparse):
    prevs = []
    num = 0
    for cid, coref in fileparse.nps.items():
        if len(prevs) > num:
            #choice = num
            # choice = random.choice(range(min(len(prevs), 5)))
            #choice = min(len(prevs), int(round(random.expovariate(1))) + 1)
            #choice = min(len(prevs), int(round(random.betavariate(1,.5))) + 1)
            choice = min(len(prevs), int(round(random.weibullvariate(1.2,7))) + 1)

            fileparse.nps[cid]['ref'] = prevs[-choice]
        prevs.append(cid)
        # antecedent = hobbs(fileparse, cid)
        # if antecedent:
        #     str_ant = ' '.join(antecedent)
        #     vprint("%s: %s -> %s" % (cid, coref['text'], str_ant))
        # 
        #     found = False
        #     for aid, ant in fileparse.nps.items():
        #         if ant['text'] == str_ant:
        #             fileparse.nps[cid]['ref'] = aid
        #             found = True
        #     if not found:
        #         aid = _mk_coref_id()
        #         fileparse.nps[aid] = {'text': str_ant}
        #         fileparse.nps[cid]['ref'] = aid


def string_matcher(fileparse):
    pass


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
    if hobbs_type == 'pronoun':
        tree = fileparse.parses[pid].ptree
        correct_type = lambda pos: (len(tree[pos]) == 1 and
                                    tree[pos].pprint().find('PRP') != -1)
        matcher = _hobbs_pronoun_match(tree[pos], pid, fileparse)
    else:
        correct_type, matcher = None, None

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

        return matches_number and matches_gender and matches_person 
    return matcher
