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
import argparse
from sys import argv
from os import strerror

def main(args):
    parses, nps = get_parses(args.listfile)
    for fid in parses.keys():
        outfile = _get_outfile_name(fid, args.responsedir)
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
    pinfo = """Satisfies final project for CS 5340/6340, University of Utah
            AUTHORS: Adam Walz (walz), Charmaine Keck (ckeck)
            For more information, please see project description
            http://www.eng.utah.edu/~cs5340/project/project.pdf"""
    parser = argparse.ArgumentParser(
        description='Coreference Resolution Engine', epilog=pinfo)
    parser.add_argument("listfile", help="File containing file path strings")
    parser.add_argument("responsedir", help="Path to output directory")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    args = parser.parse_args()

    import helpers
    helpers.mk_verbose_printer(args.verbose)
    
    from helpers import vprint
    from data import get_parses

    result = main(args)
    vprint(strerror(result))
    exit(result)