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
from sys import argv, stderr
from os import strerror


def main(args):
    parses = mk_parses(args.listfile)
    for fid in parses.keys():
        outfile = _get_outfile_name(fid, args.responsedir)
        output( find_corefs(parses[fid]), outfile )

    return 0


def find_corefs(parse):
    return format_output(parse)


def format_output(parse):
    """Takes the nps and file parse and formats the output in xml
    by listing each coreference with id and prior referent if applicable.
    
    Args:
        parse: #TODO after get_parses is written
        nps: dict, {id: (text, prior_ref)}
    
    Returns:
        string, xml markup with COREF tags

    """
    xml = '<XML>\n'
    for cid, np in parse.nps.items():
        assert np['text'], "Coref dict has no text for COREF ID='%s'" % cid
        if np.get('ref'):
            ref = " REF='%s'" % np['ref']
        else:
            ref = ''
        xml += "<COREF ID='%s'%s>%s</COREF>\n" % (cid, ref, np['text'])
    return xml + "</XML>"


def output(corefs, outfile):
    try:
        with open(outfile, 'w') as f:
            f.write(corefs)
    except IOError:
        stderr.write("Error: %s could not be written to" % outfile)


def _get_outfile_name(fid, responsedir):
    return '%s/%s.response' % (responsedir, fid)


if __name__ == '__main__':
    pinfo = """Satisfies final project for CS 5340/6340, University of Utah
            AUTHORS: Adam Walz (walz), Charmaine Keck (ckeck)
            For more information, please see project description
            http://www.eng.utah.edu/~cs5340/project/project.pdf"""
    parser = argparse.ArgumentParser(
        description='Coreference Resolution Engine', epilog=pinfo)
        
    # Get required and optional arguments
    parser.add_argument("listfile", help="File containing file path strings")
    parser.add_argument("responsedir", help="Path to output directory")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    args = parser.parse_args()

    # if verbose flag is True, create global method vprint which prints to
    # stdout only in verbose mode
    import helpers
    helpers.mk_verbose_printer(args.verbose)
    
    # Now that vprint is created, we can import the rest of the modules
    from helpers import vprint
    from data import mk_parses

    result = main(args)
    vprint(strerror(result))
    exit(result)