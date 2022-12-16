#!/usr/bin/env python3
import os, sys
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from search_variables import *
from search_functions import *


class declareVariables(search_variables):
    def __init__(self, name):
        super(declareVariables, self).__init__(name)


class Producer(Module):
    def __init__(self, **kwargs):
        # User inputs
        self.channel = kwargs.get("channel")
        self.isData = kwargs.get("dataType") == "data"
        self.year = kwargs.get("year")
        self.maxNumEvt = kwargs.get("maxNumEvt")
        self.prescaleEvt = kwargs.get("prescaleEvt")
        self.lumiWeight = kwargs.get("lumiWeight")

        # Analysis quantities
        if self.year == 2018:
            # Trigger
            print("not yet")
        elif self.year == 2017:
            # Trigger
            if self.channel == "mumu":
                self.trigger = lambda e: e.HLT_IsoMu24

        elif self.year == 2016:
            # Trigger
            if self.channel == "mumu":
                self.trigger = lambda e: e.HLT_IsoMu24

        else:
            raise ValueError("Year must be above 2016 (included).")

        # ID

        # Corrections

        # Cut flow table

    def beginJob(self):
        print("Here is beginJob")
        # pass

    def endJob(self):
        print("Here is endJob")
        # pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        print("Here is beginFile")
        self.sumNumEvt = 0
        self.sumgenWeight = 0
        self.out = declareVariables(inputFile)
        # pass

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        print("Here is endFile")
        self.out.sumNumEvt[0] = self.sumNumEvt
        self.out.sumgenWeight[0] = self.sumgenWeight
        self.out.evtree.Fill()
        self.out.outputfile.Write()
        self.out.outputfile.Close()
        # pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        # For all events
        if self.sumNumEvt > self.maxNumEvt and self.maxNumEvt != -1:
            return False
        self.sumNumEvt = self.sumNumEvt + 1
        if not self.isData:
            self.sumgenWeight = self.sumgenWeight + (
                event.genWeight / abs(event.genWeight)
            )
        if not self.sumNumEvt % self.prescaleEvt == 0:
            return False
        passCut = 0

        # Primary vertex (loose PV selection)
        if not event.PV_npvs > 0:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1  # passCut = 1

        # Trigger
        if not self.trigger(event):
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1  # passCut = 2

        # Muons
        # print("run:lumi:evt %s:%s:%s" % (event.run,event.luminosityBlock,event.event))
        muons = Collection(event, "Muon")
        selectedMusIdx = []
        selectMus(event, selectedMusIdx)
        if len(selectedMusIdx) != 2:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1  # passCut = 3
        mu0 = muons[selectedMusIdx[0]].p4()
        mu1 = muons[selectedMusIdx[1]].p4()
        if not mu0.Pt() >= 30:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1  # passCut = 4
        if not mu0.Pt() - mu1.Pt() >= 30:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1  # passCut = 5
        if not mu0.DeltaR(mu1) >= 0.3:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1  # passCut = 6
        if not (mu0 + mu1).M() >= 200:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1  # passCut = 7
        effevt(passCut, self, event)
        # print("mu0 idx pT |eta| ID Iso %s %s %s %s %s" % (selectedMusIdx[0],event.Muon_pt[selectedMusIdx[0]],abs(event.Muon_eta[selectedMusIdx[0]]),event.Muon_tightId[selectedMusIdx[0]],event.Muon_pfRelIso04_all[selectedMusIdx[0]]))
        # print("mu1 idx pT |eta| ID Iso %s %s %s %s %s" % (selectedMusIdx[1],event.Muon_pt[selectedMusIdx[1]],abs(event.Muon_eta[selectedMusIdx[1]]),event.Muon_tightId[selectedMusIdx[1]],event.Muon_pfRelIso04_all[selectedMusIdx[1]]))

        print("run:lumi:evt %s:%s:%s" % (event.run, event.luminosityBlock, event.event))
        print(
            "genWeights event.Pileup_nTrueInt %s %s"
            % (event.genWeight / abs(event.genWeight), event.Pileup_nTrueInt)
        )
        print("")

        # Event
        self.out.run[0] = event.run
        self.out.luminosityBlock[0] = event.luminosityBlock
        self.out.event[0] = event.event  # & 0xffffffffffffffff

        # Save tree
        self.out.Events.Fill()
        return True
