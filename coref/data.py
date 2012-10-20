#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
    coref.data
    ~~~~~~~~~~~~

    Parese Coreference Resolution Input file processor

    :copyright: (c) 2012 by Adam Walz, Charmaine Keck
    :license: 
"""
import pprint
from os import strerror
from errno import EIO
from xml.dom.minidom import parseString

import jsonrpc
from simplejson import loads
from nltk import sent_tokenize
from nltk.tree import Tree
from nltk.corpus import wordnet as wn

from helpers import static_var

server = jsonrpc.ServerProxy(jsonrpc.JsonRpc20(),
        jsonrpc.TransportTcpIp(addr=("127.0.0.1", 8080)))

class FilenameException(Exception):
    pass


def get_parses(listfile):
    """
    """
    
    if not listfile.find('.listfile'):
        filetype = 'Co-Reference List file'
        error = 'has incorrect file type'
        raise FilenameException("Error: %s %s" % (filetype, error))

    try:
        with open(listfile) as f:
            files = dict([(get_id(file), get_parse(file))
                for file in f.readlines() if file.lstrip()[0] != '#'])
    except IOError:
            print strerror(EIO)
            print("ERROR: Could not open list file")
            exit(EIO)
    
    parses = {}
    nps = {}
    synsets = {}
    for fid, parse in files.items():
        parses[fid], nps[fid], synsets[fid] = parse
    
    return parses, nps


def get_id(filename):
    """
    """
    fid, ext, _ = filename.strip().split('/')[-1].partition('.crf')
    if not fid or ext != '.crf':
        filetype = 'Co-Reference Input file'
        error = 'has incorrect file type'
        raise FilenameException("Error: %s %s" % (filetype, error))
    return fid


def get_parse(filename):
    """Parses input to get list of paragraphs with sentence structure
        and a dictionary of noun phrases contained in the COREF tags
        
        Returns:
            tuple, (paragraph_list, noun_phrase_dict)

    >>> get_parses("<TXT>The man ran to <COREF ID=“1”>his house</COREF></TXT>")
    ([
      (ROOT
        (S
          (NP (DT The) (NN man))
          (VP
            (VBD ran)
            (PP
              (%1 (PRP his) (NN house)) ))))],
     {1: ('his house', None)}
    )
    """
    global server
    
    try:
        with open(filename.strip()) as f:
            print 'OPEN: %s' % filename
            text = f.read()
            nps = get_tagged_corefs(text)
            text = _remove_tags(text)

            parses = []
            for sent in sent_tokenize(text):
                parse = loads(server.parse(sent))
                parse = _process_parse(parse)
                if parse:
                    parses.append(parse)
            
            pos_tags = {}
            for parse in parses:
                for word, attr in parse[1]:
                    tags = pos_tags.get(word, set())
                    tags.add(attr['PartOfSpeech'])
                    pos_tags[word] = tags
            synsets = get_synsets(pos_tags)
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(synsets)
            
            return parses, nps, synsets

    except IOError:
        print strerror(EIO)
        print("ERROR: Could not open %s" % filename)
        return ([], {})


def get_tagged_corefs(xml):
    nps = {}
    
    corefs = parseString(xml).getElementsByTagName('COREF')
    for coref in corefs:
        try:
            id = coref.attributes['ID'].value
        except KeyError:
            continue
            
        try:
            ref = coref.attributes['REF'].value
        except KeyError:
            ref = None
        
        data = coref.firstChild.data
        nps[id] = (data, ref)
    
    return nps
        

def _remove_tags(xml):
    chars = list(xml)
    
    i = 0
    while i < len(chars):
        if chars[i] == '<':
            while chars[i] != '>':
                # pop everything between brackets
                chars.pop(i)
            # pops the right-angle bracket, too
            chars.pop(i)
        else:
            i += 1
                
    return ''.join(chars)


def _process_parse(parse):
    sentence = parse.get('sentences')
    if not sentence:
        return None
    
    tree = Tree.parse(sentence[0]['parsetree'])
    words = [(w[0], w[1]) for w in sentence[0]['words']]
    dependencies = [(d[0], d[1], d[2]) for d in sentence[0]['dependencies']]
    
    return tree, words, dependencies


def get_synsets(words):
    synsets = {}
    for word in words:
        for syn in wn.synsets(word):
            synsets[syn.name] = tuple([lemma.name for lemma in syn.lemmas])
    return synsets
    
@static_var("id", '1A')
def _mk_coref_id():
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