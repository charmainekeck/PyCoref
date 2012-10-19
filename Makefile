VERSION = 0.0.1
PYTHON = /home/walz/.pythonz/pythons/CPython-2.7.3/bin/python

ROOT = /home/walz/classes/cs5340/Assignments/final
SRC_DIR = $(ROOT)/coref
RES_DIR = $(SRC_DIR)/resources
OUT_DIR = $(SRC_DIR)/output

all:
	$(PYTHON) -O coref.py $(ARGS)

dev:
	$(PYTHON) $(SRC_DIR)/coref.py $(RES_DIR)/devset/input.listfile $(OUT_DIR)

test:

clean:
	rm -f $(SRC_DIR)/*.py[co]
	rm -rf $(OUT_DIR)
