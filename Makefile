# -----------------------------------------------------------------------------
#          FILE:  Makefile
#   DESCRIPTION:  Coreference Resolution Makefule
#        AUTHOR:  Adam Walz <walz>, Charmaine Keck <ckeck>  
#       VERSION:  0.0.3
# -----------------------------------------------------------------------------
NLTK = NLTK_DATA=/home/walz/.nltk_data
PYTHON = $(NLTK) /home/walz/.pythonz/pythons/CPython-2.7.3/bin/python
CORENLP2 = 127.0.0.1
CORENLP = 155.98.111.72

FLAGS = -v -H $(CORENLP)
ROOT = /home/walz/classes/cs5340/Assignments/final
SRCDIR   = $(ROOT)/coref
RESDIR   = $(HOME)/Public/resources
OUTDIR   = $(HOME)/Public/outdir
EXEC     = $(SRCDIR)/coref.py

DLISTFILE = $(RESDIR)/devset/input.listfile
DOUTLIST  = $(RESDIR)/devset/output.listfile
DKEYDIR   = $(RESDIR)/devset/officialkeys

S1LISTFILE = $(RESDIR)/set1/inlist
S1OUTLIST  = $(RESDIR)/set1/output.listfile
S1KEYDIR   = $(RESDIR)/set1/officialkeys

SCORER   = $(RESDIR)/coref-scorer.py

all:
	$(PYTHON) -O coref/coref.py $(ARGS) $(FLAGS)

dev:
	$(PYTHON) $(EXEC) $(DLISTFILE) $(OUTDIR) $(FLAGS)

debug:
	$(PYTHON) -m pdb $(EXEC) $(S1LISTFILE) $(OUTDIR) $(FLAGS)

dev-score: dev
	$(PYTHON) $(SCORER) $(DOUTLIST) $(DKEYDIR) 

set1:
	$(PYTHON) $(EXEC) $(S1LISTFILE) $(OUTDIR) $(FLAGS)

set1-score: set1
	$(PYTHON) $(SCORER) $(S1OUTLIST) $(S1KEYDIR)-VV

doctests:
	$(PYTHON) $(EXEC) $(DLISTFILE) $(DOUTDIR) -t $(FLAGS)

clean:
	rm -f $(SRCDIR)/*.py[co]
	rm -rf $(OUTDIR)/*
