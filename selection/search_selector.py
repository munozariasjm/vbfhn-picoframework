#!/usr/bin/env python3
import os
import sys
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from search_variables import *
from search_functions import *


class declareVariables(search_variables):
    def __init__(self) -> None:
        super(declareVariables, self).__init__()


class Producer(Module):
    def __init__(self, **kwargs):
        # From Arguments
        self.channel = kwargs.get("channel")
        self.isData = kwargs.get("dataType") == "data"
        self.year = kwargs.get("year")
        self.maxNumEvt = kwargs.get("maxNumEvt")
        self.prescaleEvt = kwargs.get("prescaleEvt")
        self.lumiWeight = kwargs.get("lumiWeight")

        # Other parameters
        self.objectClearningDr = 0.5
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

    def beginJob(self):
        print("Here is beginJob")

    def endJob(self):
        print("Here is endJob")

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        print("Here is beginFile")
        self.sumNumEvt = 0
        self.sumgenWeight = 0
        self.out = declareVariables(inputFile)

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        print("Here is endFile")
        self.out.sumNumEvt[0] = self.sumNumEvt
        self.out.sumgenWeight[0] = self.sumgenWeight
        self.out.evtree.Fill()
        self.out.outputfile.Write()
        self.out.outputfile.Close()

    def analyze(self, event):
        """process event, return True (go to next module) or
        False (fail, go to next event)"""
        if self.maxNumEvt > 0 and self.sumNumEvt >= self.maxNumEvt:
            return False
        self.sumNumEvt += 1
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
        #  #Trigger
        #  if not self.trigger(event):
        #      effevt(passCut,self,event)
        #      return False
        #  passCut = passCut+1 #passCut = 2
        print(f"run:lumi:evt {event.run}:{event.luminosityBlock}:{event.event}")

        # Taus
        taus = Collection(event, "Tau")
        selectedTausIdx = []
        selectTaus(event, selectedTausIdx)
        print(len(selectedTausIdx))
        if not (
            len(selectedTausIdx) == 2
            and taus[selectedTausIdx[0]].p4().DeltaR(taus[selectedTausIdx[1]].p4())
            >= self.objectClearningDr
        ):  # no charge requirement atm
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1
        selectedElesIdx = []
        selectEles(event, selectedElesIdx, selectedTausIdx, self.objectClearningDr)
        if not len(selectedElesIdx) == 0:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1
        # Mu veto
        selectedMusIdx = []
        selectMus(event, selectedMusIdx, selectedTausIdx, self.objectClearningDr)
        if not len(selectedMusIdx) == 0:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1
        # Jets
        selectedWJetsIdx = []
        selectFatJets(event, year, selectedTausIdx, selectedWJetsIdx)
        selectedJetsIdx = []
        selectedTightBIdx = []
        selectJets(
            event,
            year,
            selectedTausIdx,
            selectedWJetsIdx,
            selectedJetsIdx,
            selectedTightBIdx,
            objectClearningDr,
        )
        # Event
        self.out.run[0] = event.run
        self.out.luminosityBlock[0] = event.luminosityBlock
        self.out.event[0] = event.event  # & 0xffffffffffffffff

        # Save tree
        self.out.Events.Fill()
        return True
