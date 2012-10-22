#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
    coref.helpers
    ~~~~~~~~~~~~

    Helper functions used in coreference resolution

    :copyright: (c) 2012 by Adam Walz, Charmaine Keck
    :license: 
"""

def static_var(varname, value):
    """Mimics a static variable"""
    def decorate(func):
        setattr(func, varname, value)
        return func
    return decorate

def mk_verbose_printer(verbose):
    """Creates a global verbose print method named vprint if verbose flag
    is set. If verbose flag is set, vprint mimics the builtin print statment.
    If verbose flag is not set, vprint does nothing.
    
    Args:
        verbose, boolean if verbose flag is set
    """
    global vprint
    if verbose:
        def vprint(*args):
            # Print each argument separately so caller doesn't need to
            # stuff everything to be printed into a single string
            for arg in args:
               print arg,
            print
    else:
        vprint = lambda *a: None      # do-nothing function
