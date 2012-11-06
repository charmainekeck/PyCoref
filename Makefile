# -----------------------------------------------------------------------------
#          FILE:  Makefile
#   DESCRIPTION:  Coreference Resolution Makefule
#        AUTHOR:  Adam Walz <walz>, Charmaine Keck <ckeck>  
#       VERSION:  0.0.3
# -----------------------------------------------------------------------------
NLTK = NLTK_DATA=/home/walz/.nltk_data
PYTHON = $(NLTK) /home/walz/.pythonz/pythons/CPython-2.7.3/bin/python
CORENLP = 155.98.111.72

FLAGS = -v -H $(CORENLP)
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
	$(PYTHON) -O coref.py $(ARGS) $(FLAGS)

dev:
	$(PYTHON) $(EXEC) $(LISTFILE) $(OUTDIR) $(FLAGS)

debug:
	$(PYTHON) -m pdb $(EXEC) $(LISTFILE) $(OUTDIR) $(FLAGS)

dev-score: dev
	$(PYTHON) $(SCORER) $(OUTLIST) $(KEYDIR) $(FLAGS)

set1:
	$(PYTHON) $(EXEC) $(LISTFILE:devset=set1) $(OUTDIR)

set1-score: set1
	$(PYTHON) $(SCORER) -d $(OUTLIST:devset=set1) $(KEYDIR:devset=set1) $(FLAGS)

doctests:
	$(PYTHON) $(EXEC) $(LISTFILE) $(OUTDIR) -t $(FLAGS)

clean:
	rm -f $(SRCDIR)/*.py[co]
	rm -rf $(OUTDIR)/*
