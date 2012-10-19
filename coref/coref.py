#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""This file contains a utility for Co-Reference Resolution

Written for CS 5340/6340 Final Project
Adam Walz (walz)
Charmaine Keck (ckeck)

Copyright 2012 Adam Walz, Charmaine Keck

This file contains class definitions for:
"""

from sys import argv

def main():
    try:
        listfile = argv[1]
        responsedir = argv[2]
    except IndexError:
        print("ERROR: Not enough arguments")
        return 1

    try:
        with open(listfile) as f:
            pass
    except IOError:
            print("ERROR: Could not open list file")
            exit(1)

    return 0

if __name__ == '__main__':
    exit(main())