# -----------------------------------------------------------------------------
#          FILE:  Makefile
#   DESCRIPTION:  Coreference Resolution Makefule
#        AUTHOR:  Adam Walz <walz>, Charmaine Keck <ckeck>  
#       VERSION:  0.0.2
# -----------------------------------------------------------------------------
PYTHON = /home/walz/.pythonz/pythons/CPython-2.7.3/bin/python

ROOT = /home/walz/classes/cs5340/Assignments/final
SRCDIR   = $(ROOT)/coref
RESDIR   = $(HOME)/Public/resources
OUTDIR   = $(HOME)/Public/outdir
EXEC     = $(SRCDIR)/coref.py
LISTFILE = $(RESDIR)/devset/input.listfile
OUTLIST  = $(RESDIR)/devset/output.listfile
KEYDIR   = $(RESDIR)/devset/officialkeys
SCORER   = $(RESDIR)/coref-scorer.py

all:
	$(PYTHON) -O coref.py $(ARGS)

dev:
	$(PYTHON) $(EXEC) $(LISTFILE) $(OUTDIR)

dev-score: dev
	$(PYTHON) $(SCORER) $(OUTLIST) $(KEYDIR) -V

set1:
	$(PYTHON) $(EXEC) $(LISTFILE:devset=set1) $(OUTDIR)

set1-score: set1
	$(PYTHON) $(SCORER) -d $(OUTLIST:devset=set1) $(KEYDIR:devset=set1) -V

test:

clean:
	rm -f $(SRCDIR)/*.py[co]
	rm -rf $(OUTDIR)/*
