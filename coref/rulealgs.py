# -*- coding: utf-8 -*-
"""
    coref.rulealgs
    ~~~~~~~~~~~~

    Algorithms for rule based for coreference resolution

    :copyright: (c) 2012 by Adam Walz, Charmaine Keck
    :license:
"""

from nltk.tree import Tree

from data import _mk_coref_id
from helpers import vprint

def apply_rules(fileparse):
    for cid, coref in fileparse.nps.items():
        antecedent = hobbs(fileparse, cid)
        if antecedent:
            str_ant = ' '.join(antecedent)
            vprint("%s: %s -> %s" % (cid, coref['text'], str_ant))
def string_matcher(fileparse):
    pass


def hobbs(fileparse, coref_id):
    # Begin at NP immediately dominating the pronound
    treeid, pos, tree = _get_dominating_np(fileparse, coref_id)

    if treeid is None or not pos:
        return None

    # Go up tree to first NP or S.
    pos, path = _go_up_to_S_or_NP(tree, pos)

    # Traverse all branches below pos to the left of path.
    proposal, path = _traverse(tree, pos, path)

    while not proposal:
        # If pos is the highest S in the sentence,
        if pos == (0,):
            # traverse the parse trees of the previous sentences
            # in the order of recency.
            if treeid == 0:
                return None
            treeid -= 1
            tree = fileparse.parses[treeid].ptree

            # Traverse left-to-right, breadth first.
            # When a NP is encountered, propose as antecedent.
            proposal, path = _traverse(tree, (), [])

        else:
            # From node pos, go up the tree to the first NP or S.
            pos, path = _go_up_to_S_or_NP(tree, pos)

        # If pos is an NP and the path to pos did not pass through the nominal
        # that pos immediately dominates, propose pos as antecedent
        if tree[pos].node == 'NP':
            passes_through = False
            for i in range(len(tree[pos])):
                temp_pos = pos + (i,)
                if tree[temp_pos].node.startswith('N') and temp_pos in path:
                    passes_through = True
            if not passes_through:
                proposal = pos

        # Traverse all branches below pos to the left of the path
        # Propose any NP encountered as the antecdent
        new_p, path = _traverse(tree, pos, path)
        if new_p:
            proposal = new_p

        # If pos is an S node, traverse to the right of path, but do not go
        # below any NP or S node.
        # Propose any NP node as antecedent
        if tree[pos].node == 'S':
            new_p, path = _traverse(tree, pos, path, direction='right')
            if new_p:
                proposal = new_p

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


def _traverse(tree, pos, path, direction='left'):
    proposal = None

    # bounds checks if position is left of the path (path implies 2 nodes)
    if direction == 'left':
        bounds = lambda p: len(path) < 2 or p < path[-2]
    else:
        bounds = lambda p: len(path) < 2 or p > path[-2]

    new_path = path[:]
    for sub_pos in tree[pos].treepositions():
        p = pos + sub_pos
        if isinstance(tree[p], Tree) and bounds(p) and p not in path:
            new_path.append(p)

            if direction == 'right':
                if tree[p].node == 'NP' or tree[p].node == 'S':
                    break

            # Propose any NP that has a NP or S between it and pos
            if tree[p].node == 'NP':
                proposal = p
    return proposal, new_path


def _go_up_to_S_or_NP(tree, pos):
    pos = pos[:-1]
    path = [pos]
    while tree[pos].node != 'S' and tree[pos].node != 'NP':
        pos = pos[:-1]
        path.append(pos)
    return pos, path
