#!/usr/bin/python
# Scoring program for CS 5340/6340 coreference resolution project. 
# Usage: ./coref-scorer.py -d [response dir] [key dir] -v
#
import sys
import re
import copy
import xml.sax
from xml.sax.handler import ContentHandler

#useful globals
VERBOSE = False
VVERBOSE = False
GOLDPRONOUN = 0
GOLDCOMMON = 0
GOLDPROPER = 0
simplePronouns = []
personPronouns = []
neuteredPronouns = []
reflexivePronouns = []
uppercase = re.compile(".*[A-Z].*")

class Entity:
   def __init__(self):
      self.id = ""
      self.referents = []
      self.text = ""
      self.min = ""
      self.start = -1
      self.end = -1

   def __str__(self):
      return "%s (%s)" % (self.text, self.id)

   def getId(self):
      return self.id

class corefHandler(ContentHandler):
   def __init__(self):
      self.entities = {}
      self.inCorefTag = 0
      self.strings = []
      self.ids = []
      self.fullText = ""
      self.currentByte = 0
      self.totalMarkables = 0

   def startElement(self, name, attr):
      if name == "COREF" or name == "coref":
         self.totalMarkables += 1
         self.inCorefTag = self.inCorefTag + 1
         self.strings.append("")
         
         if str(attr["ID"]) not in self.entities.keys():
            e = Entity()
            e.id = attr["ID"]
            e.start = self.currentByte
            e.referents.append(attr.get("REF", ""))

            self.entities[str(e.getId())] = copy.deepcopy(e)
            self.ids.append(attr["ID"])
         else:
            print "Error...duplicate id found: %s" % (attr["ID"])
            print "Please choose a different id for this np."
            sys.exit(1)

   def endElement(self, name):
      if name == "COREF" or name == "coref":
         self.inCorefTag = self.inCorefTag - 1
         id = self.ids.pop()
         self.entities[id].text = self.strings.pop().replace("\n", " ")
         self.entities[id].end = self.currentByte

   def characters(self, ch):
      if self.inCorefTag > 0:
         for i in range(0, len(self.strings)):
            self.strings[i] = self.strings[i] + ch
      self.fullText += ch
      self.currentByte += len(ch)

def inChain(a, k):
   """Returns true if anaphor is a member of this chain."""
   for np in k:
      if (a.id == np.id):
         return k.index(np)
   return -1

def spans(ant, anchor):
   """Returns true if antecedent does not exceed the full span and contains at least the minimum needed."""

   if anchor.min != "":
      if (ant.find(anchor.min) > -1) and (anchor.text.find(ant) > -1):
         return True
      else:
         if anchor.text == ant:
            return True
   else:
      if anchor.text.find(ant) > -1:
         return True

   return False

def pronounCheck(phrase):
   global simplePronouns, personPronouns, neuteredPronouns, reflexivePronouns
   if phrase in simplePronouns:
      return True
   elif phrase in personPronouns:
      return True
   elif phrase in neuteredPronouns:
      return True
   elif phrase in reflexivePronouns:
      return True
   else:
      return False

def commonCheck(phrase):
   global uppercase
   if (not uppercase.match(phrase)):
      return True
   return False

def properCheck(phrase):
   global uppercase
   if uppercase.match(phrase) and ((not phrase.find("The ") > -1) or (not phrase.find("A ") > -1)) :
      return True
   return False

def score(resolutions, keys):
   """Returns the number of correct resolutions for a given document."""
   global GOLDPROPER
   global GOLDPRONOUN
   global GOLDCOMMON
   global VVERBOSE
   correct = 0        #the total number of correctly resolved anaphora.
   pronouns = 0       #the total number of pronouns resolved correctly resolved.
   common = 0         #the total number of common nouns correctly resolved.
   proper = 0         #the total number of proper nouns correctly resolved.
   for r in resolutions.keys():
      anaphor = r
      antecedent = resolutions[r]

      #check for matching ids, if the anaphor and antecedent have the same id then don't allow
      #them to resolve.
      if (anaphor.id == antecedent.id):
         if VVERBOSE:
            print "Error: Anaphor and Antecedent have same id...will not be counted. (%s, %s)" % (anaphor.text, antecedent.text)
         continue

      for k in keys:
         index = inChain(anaphor, k)
         if index > -1:
            #check for the easy case, the anaphor is resolved with another
            #non-anchor anaphor.
            if antecedent.id in map(lambda x : x.id, k[:index]):
            #if antecedent.id in map(lambda x : x.id, k):
               if VVERBOSE:
                  print "RESOLVED: %s (%s) <= %s (%s)" % (antecedent.text, antecedent.id, anaphor.text, anaphor.id)
               correct += 1
               if pronounCheck(anaphor.text.lower()):
                  pronouns += 1
               elif commonCheck(anaphor.text):
                  common += 1
               elif properCheck(anaphor.text):
                  proper += 1
               break
            
            #anchor antecedent case.
            #if spans(antecedent.text, k[:index]):
            if spans(antecedent.text, k[0]):
               if VVERBOSE:
                  print "RESOLVED: %s (%s) <= %s (%s)" % (antecedent.text, antecedent.id, anaphor.text, anaphor.id)
               correct += 1
               if pronounCheck(anaphor.text.lower()):
                  pronouns += 1
               elif commonCheck(anaphor.text):
                  common += 1
               elif properCheck(anaphor.text):
                  proper += 1
               break
   if VERBOSE:
      if GOLDPRONOUN != 0:
         print "Number of pronouns resolved: %d (%0.2f)" % (pronouns, float(pronouns)/GOLDPRONOUN)
      else:
         print "There are no pronouns to resolve in this document."
      if GOLDCOMMON != 0:
         print "Number of common nouns resolved: %d (%0.2f)" % (common, float(common)/GOLDCOMMON)
      else:
         print "There are no common nouns to resolve in this document."
      if GOLDPROPER != 0:
         print "Number of proper nouns resolved: %d (%0.2f)" % (proper, float(proper)/GOLDPROPER)
      else:
         print "There are no proper nouns to resolve in this document."

   return correct

def main(args):
   """Where the magic happens."""
   if len(args) < 3:
      print "Usage: %s response-list keydir [-V]" % args[0]
      print "-v : Verbose mode."
      print "-VV : Very Verbose mode."
      sys.exit(1)

   #some pronoun classes globals
   global simplePronouns
   global personPronouns
   global neuteredPronouns
   global reflexivePronouns
   global GOLDPROPER
   global GOLDPRONOUN
   global GOLDCOMMON
   global VERBOSE
   global VVERBOSE
   simplePronouns = ("he", "her", "his", "hers", "him")
   personPronouns = ("i", "we", "you")
   neuteredPronouns = ("its", "it", "they", "them", "theirs", "their")
   reflexivePronouns = ("himself", "themselves", "herself", "itself")
   totalCorrect = 0
   totalResolutions = 0

   #read in files
   try:
      responseList = open(args[1],'r')
   except:
      print "Error 1...file not found: %s" % (args[1])
      sys.exit(1)

   if ("-v" in args) or ("-V" in args):
      VERBOSE = True
   elif ("-vv" in args) or ("-VV" in args):
      VERBOSE = True
      VVERBOSE = True

   #read in files
   filelst = []
   for line in responseList:
      line = line.strip()
      filelst.append(line)
   responseList.close()
   
   for f in filelst:
      GOLDCOMMON = 0
      GOLDPRONOUN = 0
      GOLDPROPER = 0

      #set up XML parser
      parser = xml.sax.make_parser()
      handler = corefHandler()
      parser.setContentHandler(handler)

      try:
         inFile = open(f, 'r')
      except:
         print "Error 2...file not found: %s" % (f)
         sys.exit(1)

      #parse the file
      try:
         parser.parse(inFile)
      except:
         print "Error...XML syntax on file: %s, check for mismatched tags..." % (f)
         sys.exit(1)
      inFile.close()
      
      #gather all response resolutions
      resolutions = {}
      responseResolutionCount = 0
      entities = handler.entities

      doc = ""
      if f.find("/") > -1:
         doc = f[f.rfind("/")+1:].replace(".response",".key").replace(".fkey", ".key").replace(".crf",".key")
      else:
         doc = f.replace(".response",".key").replace(".fkey", ".key").replace(".crf",".key")

      if args[2][-1] != "/":
         keyInFile = args[2] + "/" + doc
      else:
         keyInFile = args[2] + doc

      try:
         keyFile = open(keyInFile, 'r')
      except:
         print "Error...keyfile not found: %s" % (keyInFile)
         sys.exit(1)

      for e in entities.keys():
         if entities[str(e)].referents[0] != '':
            ref = entities[str(e)].referents[0]
            resolutions[entities[e]] = entities[str(ref)]
            responseResolutionCount += 1

      #read in the key
      keyResolutionCount = 0
      keyEntities = []
      for line in keyFile:
         if line[0] == "#":
            continue
         line = line.strip()
         if line.count("$!$") <= 1:
            continue

         keyResolutionCount += line.count("$!$") - 1
         tokens = line.split("$!$")
         tmp = []
         for t in tokens:
            if t == '':
               continue
            e = Entity()
            e.text = t[:t.index("]")].replace("[","").strip()
            e.min = t[t.index("(")-1:t.index(")")].replace("(","").strip()
            e.id = t[t.index("{")-1:t.index("}")].replace("{","").strip()
            tmp.append(copy.deepcopy(e))

            #gather some stats on anaphora
            if tokens.index(t) != 0:
               if pronounCheck(e.text.lower()):
                  GOLDPRONOUN += 1
               elif commonCheck(e.text):
                  GOLDCOMMON += 1
               elif properCheck(e.text):
                  GOLDPROPER += 1
         keyEntities.append(tmp)
      keyFile.close()
      totalResolutions += keyResolutionCount

      #doing the scoring
      correct = score(resolutions, keyEntities)
      totalCorrect += correct

      if VERBOSE:
         print "Response resolutions: %d" % responseResolutionCount
         print "Truth resolutions: %d" % keyResolutionCount
         print "Total correct: %d" % correct
      print "Document %s Score:  %0.2f" % (doc.replace(".key",""), float(correct)/keyResolutionCount)
      if VERBOSE:
         print 

   print "-------------------------------------------------"
   print "Final accuracy score: %0.4f" % (float(totalCorrect)/totalResolutions)
   print "-------------------------------------------------"

if __name__ == "__main__": main(sys.argv)
