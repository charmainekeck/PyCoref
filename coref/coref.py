#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""This file contains a utility for Co-Reference Resolution

Written for CS 5340/6340 Final Project
Adam Walz (walz)
Charmaine Keck (ckeck)

Copyright 2012 Adam Walz, Charmaine Keck

This file contains class definitions for:
"""

import errno
from sys import argv
from os import strerror

from data import get_parses

def main():
    try:
        listfile = argv[1]
        responsedir = argv[2]
    except IndexError:
        print("ERROR: Not enough arguments")
        return errno.EINVAL

    parses, nps = get_parses(listfile)
    
    for fid in parses.keys():
        outfile = _get_outfile_name(fid, responsedir)
        output( find_corefs(parses[fid], nps[fid]), outfile )

    return 0


def find_corefs(parse, nps):
    return '<TXT></TXT>'


def output(corefs, outfile):
    try:
        with open(outfile, 'w') as f:
            f.write(corefs)
    except IOError:
        print "Error: %s could not be written to" % outfile


def _get_outfile_name(fid, responsedir):
    return '%s/%s.response' % (responsedir, fid)


if __name__ == '__main__':
    result = main()
    print strerror(result)
    exit(result)