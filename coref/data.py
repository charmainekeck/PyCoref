#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
    coref.data
    ~~~~~~~~~~~~

    Parese Coreference Resolution Input file processor

    :copyright: (c) 2012 by Adam Walz, Charmaine Keck
    :license: 
"""

from errno import EIO
from os import strerror

from helpers import static_var

class FilenameException(Exception):
    pass


def get_parses(listfile):
    """
    """
    
    if not listfile.find('.listfile'):
        filetype = 'Co-Reference List file'
        error = 'has incorrect file type'
        raise FilenameException("Error: %s %s" % (filetype, error))

    parses = {}
    nps = {}
    try:
        with open(listfile) as f:
            for filename in f.readlines():
                fid = get_id(filename)
                parses[fid], nps[fid] = get_parse(filename)
    except IOError:
            print strerror(EIO)
            print("ERROR: Could not open list file")
            exit(EIO)
    
    return parses, nps


def get_id(filename):
    """
    """
    fid, ext, _ = filename.split('/')[-1].partition('.crf')
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
     {1: None}
    )
    """
    return (None, None)

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