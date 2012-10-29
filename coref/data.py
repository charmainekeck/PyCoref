#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
    coref.data
    ~~~~~~~~~~~~

    Parese Coreference Resolution Input file processor

    :copyright: (c) 2012 by Adam Walz, Charmaine Keck
    :license: 
"""
import re
from os import strerror
from errno import EIO
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError

import jsonrpc
from simplejson import loads
from nltk import sent_tokenize, word_tokenize
from nltk.tree import Tree
from nltk.corpus import wordnet as wn

from helpers import static_var, vprint

class FileParse():
    def __init__(self, filename, pserver):
        fparse = mk_fparse(filename.strip(), pserver)
        self.parses = [Parse(p) for p in fparse[0]]
        self.nps = fparse[1]
        self.synsets = fparse[2]


class Parse():
    def __init__(self, parse):
        self.ptree = parse[0]
        self.words = parse[1]
        self.dependencies = parse[2]
        self.text = parse[3]


class FilenameException(Exception):
    pass


def mk_parses(listfile):
    """
    """
    
    if not listfile.endswith('.listfile'):
        filetype = 'Co-Reference List file'
        error = 'has incorrect file type'
        raise FilenameException("Error: %s %s" % (filetype, error))

    try:
        with open(listfile) as f:
            pserver = jsonrpc.ServerProxy(jsonrpc.JsonRpc20(),
                    jsonrpc.TransportTcpIp(addr=("127.0.0.1", 8080)))
            parses = dict([(get_id(file), FileParse(file, pserver))
                for file in f.readlines() if file.lstrip()[0] != '#'])
    except IOError:
            stderr.write(strerror(EIO))
            stderr.write("\nERROR: Could not open list file\n")
            exit(EIO)
    else:
        return parses


def get_id(path):
    """Parses a file path for the filename without extension
    
    Args:
        path: string, full (or relative) file path for coreference file.
              Must end in .crf
    
    Returns:
        string, file id (filename without extension)
        
    >>> path = '/home/user/Desktop/full.crf'
    >>> get_id(path)
    'full'
    
    >>> path = 'relative.crf'
    >>> get_id(path)
    'relative'
    
    """
    fid, ext, _ = path.strip().split('/')[-1].partition('.crf')
    if not fid or ext != '.crf':
        filetype = 'Co-Reference Input file'
        error = 'has incorrect file type'
        raise FilenameException("Error: %s %s" % (filetype, error))
    return fid


def mk_fparse(filename, pserver):
    """Parses input to get list of paragraphs with sentence structure
        and a dictionary of noun phrases contained in the COREF tags
        
        Returns:
            tuple, (paragraph_list, noun_phrase_dict)
    """
    global server
    
    try:
        with open(filename.strip()) as f:
            print 'OPEN: %s' % filename
            xml = f.read()
            nps = get_tagged_corefs(xml)
            rawtext = _remove_tags(xml)

            parses = []
            for sent in sent_tokenize(rawtext):
                parses.append(loads(pserver.parse(sent.strip())))
            parses = _process_parses(parses, nps)

            pos_tags = {}
            for parse in parses:
                for word, attr in parse[1]:
                    tags = pos_tags.get(word, set())
                    tags.add(attr['PartOfSpeech'])
                    pos_tags[word] = tags
            synsets = get_synsets(pos_tags)
            
            return parses, nps, synsets

    except IOError:
        print strerror(EIO)
        print("ERROR: Could not open %s" % filename)
        return ([], {})


def tag_ptrees(ptrees, corefs):
    tag_trees = ptrees[:]
    currparse = 0
    pattern =  r'(?P<lp>\(?\s*)(?P<tg>\w+)?(?P<data>\s*%s)(?P<rp>(?:\s*\))*)'

    for cid, coref in corefs.items():
        words = word_tokenize(coref['text'])
        for tree in ptrees[currparse:]:
            dpattern = r'\s*'.join([r'\(\s*[a-zA-Z$]+\s+%s\s*\)' % word
                        for word in words])
            
            found = re.findall(pattern % dpattern, tree)
            if found:
                params = found[0][0], found[0][1], cid, found[0][2], found[0][3]
                repl = '%s%s (COREF_TAG_%s %s ) %s' % params
                tag_trees[currparse] = re.sub(pattern % dpattern, repl, tree, 1)
                break
            else:
                currparse += 1

    return tag_trees


def get_tagged_corefs(xml, ordered=False):
    """Parses xml to find all tagged coreferences contained in COREF tags
        
        Args:
            xml: string, xml markedup with COREF tags

        Returns:
            dict, {coref_id: (coref, ref_id)
    
    >>> text = "<TXT>John stubbed <COREF ID='1'>his</COREF> toe.</TXT>"
    >>> get_tagged_corefs(text)
    {u'1': (u'his', None)}
    
    >>> text = "<TXT><COREF ID='A'>John</COREF> stubbed " +\
                "<COREF ID='1' REF='A'>his</COREF> toe.</TXT>"
    >>> get_tagged_corefs(text)
    {u'A': (u'John', None), u'1': (u'his', u'A')}
    
    """

    if ordered:
        nps = []
    else:
        nps = {}
    
    xml = xml.strip()
    if not xml.startswith('<TXT>'):
        xml = '<TXT>' + xml
    if not xml.endswith('</TXT>'):
        xml = xml + '</TXT>'
    try:
        corefs = parseString(xml).getElementsByTagName('COREF')
    except ExpatError:
        return nps

    for coref in corefs:
        try:
            cid = coref.attributes['ID'].value
            if ordered:
                data = {}
                for npid, np in nps:
                    if npid == cid:
                        data = np
                        break
            else:
                data = nps.get(cid, {})
        except KeyError:
            continue
            
        try:
            data['ref'] = coref.attributes['REF'].value
        except KeyError:
            data['ref'] = None
        
        data['text'] = coref.firstChild.data
        if ordered:
            nps.append((cid, data))
        else:
            nps[cid] = data
    
    return nps


def _remove_tags(xml):
    """Removes xml tags from string, returning non-markedup text
        
        Args:
            xml: string, xml markedup text

        Returns:
            string, text from xml
    
    >>> xml = "<TXT>John stubbed <COREF ID='1'>his</COREF> toe.</TXT>"
    >>> _remove_tags(xml)
    'John stubbed his toe.'
    
    >>> xml = "<TXT><COREF ID='A'>John</COREF> stubbed " +\
                "<COREF ID='1' REF='A'>his</COREF> toe.</TXT>"
    >>> _remove_tags(xml)
    'John stubbed his toe.'
    
    """
    chars = list(xml)
    
    i = 0
    while i < len(chars):
        if chars[i] == '<':
            while chars[i] != '>':
                chars.pop(i) # pop everything between brackets
            chars.pop(i) # pops the right-angle bracket, too
        else:
            i += 1
                
    return ''.join(chars)


def _process_parses(parses, nps):
    ptrees = []
    for parse in parses:
        sentence = parse.get('sentences')
        if sentence:
            ptrees.append(sentence[0]['parsetree'])
    ptrees = tag_ptrees(ptrees, nps)
    
    pparses = []
    for parse in parses:
        sentence = parse.get('sentences')
        if sentence:
            tree = Tree.parse(ptrees.pop(0))
            words = [(w[0], w[1]) for w in sentence[0]['words']]
            depends = [(d[0], d[1], d[2]) for d in sentence[0]['dependencies']]
            text = sentence[0]['text']
            
            pparses.append((tree, words, depends, text))
    
    return pparses


def get_synsets(words):
    """Returns sets of cognitive synonyms for each of the input words
        
        Args:
            words: dict, {word: (pos1, pos2, ...)}

        Returns:
            dict, {synset_name: (syn1, syn2, syn3, ...)}
    
        >>> words = {u'apple': (u'NN')}
        >>> get_synsets(words) # doctest: +NORMALIZE_WHITESPACE
        {'apple.n.01': ('apple',), \
         'apple.n.02': ('apple', 'orchard_apple_tree', 'Malus_pumila')}
    
    """
    synsets = {}
    for word in words:
        for syn in wn.synsets(word):
            synsets[syn.name] = tuple([lemma.name for lemma in syn.lemmas])
    return synsets
    
@static_var("id", '1A')
def _mk_coref_id():
    """Creates a unique coreference id tag
    
    Note: only unique if input id's are not of the form num+alpha
    
    """
    num, alpha = int(_mk_coref_id.id[:-1]), _mk_coref_id.id[-1]
    if alpha == 'Z':
        alpha = 'A'
        num += 1
    else:
        alpha = chr(ord(alpha) + 1)
    
    return _mk_coref_id.id
            
if __name__ == '__main__':
    import doctest
    doctest.testmod()
