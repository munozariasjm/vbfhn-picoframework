#!/usr/bin/env python3
import os, sys
import ROOT
import math
import numpy as np


class search_variables(object):
    def __init__(self, name):

        # Create file
        inputFile = name
        outputFileName = (
            os.path.basename(str(inputFile)).split(".root", 1)[0] + "_Skim.root"
        )
        compression = "LZMA:9"
        ROOT.gInterpreter.ProcessLine("#include <Compression.h>")
        (algo, level) = compression.split(":")
        compressionLevel = int(level)
        if algo == "LZMA":
            compressionAlgo = ROOT.ROOT.kLZMA
        elif algo == "ZLIB":
            compressionAlgo = ROOT.ROOT.kZLIB
        else:
            raise RuntimeError("Unsupported compression %s" % algo)
        self.outputfile = ROOT.TFile(outputFileName, "RECREATE", "", compressionLevel)
        self.outputfile.SetCompressionAlgorithm(compressionAlgo)

        # All entries
        self.evtree = ROOT.TTree("evtree", "evtree")
        self.add_float(self.evtree, "sumNumEvt")
        self.add_float(self.evtree, "sumgenWeight")

        # Efficiency/Num events
        self.effevt = ROOT.TTree("effevt", "effevt")
        self.add_float(self.effevt, "passCut")
        self.add_float(self.effevt, "eegenWeight")
        self.add_float(self.effevt, "eelumiWeight")

        # Common variables
        self.Events = ROOT.TTree("Events", "Events")
        self.add_float(self.Events, "run")
        self.add_float(self.Events, "luminosityBlock")
        self.add_float(self.Events, "event")
        self.add_float(self.Events, "genWeight")
        self.add_float(self.Events, "lumiWeight")

    def add_float(self, tree, name, dtype=np.dtype(float)):
        if hasattr(self, name):
            print('ERROR! SetBranchAddress of name "%s" already exists!' % (name))
            exit(1)
        setattr(
            self,
            name,
            np.full(
                (1), -99999999999999999999999999999999999999999999999999, dtype=dtype
            ),
        )  # 1 elem w/ inizialization '-99999999999999999999999999999999999999999999999999'
        tree.Branch(
            name, getattr(self, name), "{0}/D".format(name)
        )  # The types in root (/D in this example) are defined here https://root.cern/root/html528/TTree.html

    def add_string(
        self, tree, name, dtype=np.dtype("S100")
    ):  # It assumes a string of max 100 characters
        if hasattr(self, name):
            print('ERROR! SetBranchAddress of name "%s" already exists!' % (name))
            exit(1)
        setattr(
            self, name, np.full((1), "noVal", dtype=dtype)
        )  # 1 elem w/ inizialization 'noval'
        tree.Branch(name, getattr(self, name), "{0}/C".format(name))

    def add_vectorFloat(self, tree, name):
        if hasattr(self, name):
            print('ERROR! SetBranchAddress of name "%s" already exists!' % (name))
            exit(1)
        setattr(self, name, ROOT.std.vector("float")())  # No inizialization
        tree.Branch(name, getattr(self, name))

    def add_vectorString(self, tree, name):
        if hasattr(self, name):
            print('ERROR! SetBranchAddress of name "%s" already exists!' % (name))
            exit(1)
        setattr(self, name, ROOT.std.vector("string")())  # No inizialization
        tree.Branch(name, getattr(self, name))
