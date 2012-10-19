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

def main():
    try:
        listfile = argv[1]
        responsedir = argv[2]
    except IndexError:
        print("ERROR: Not enough arguments")
        return errno.EINVAL

    try:
        with open(listfile) as f:
            pass
    except IOError:
            print("ERROR: Could not open list file")
            return errno.EIO

    return 0

if __name__ == '__main__':
    result = main()
    print strerror(result)
    exit(result)