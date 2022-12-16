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
        # self.isData      = kwargs.get('dataType')=='data'
        self.isData = "data" in kwargs.get("dataType")
        self.year = kwargs.get("year")
        self.maxNumEvt = kwargs.get("maxNumEvt")
        self.prescaleEvt = kwargs.get("prescaleEvt")
        self.processName = kwargs.get("processName")
        self.lumiWeight = kwargs.get("lumiWeight")
        self.DataRun = kwargs.get("dataType")

        # print("dataType %s" % self.DataRun)
        # if self.isData:
        # runperiod = processName.replace(datasets_info[d][1],'')
        # dataType="data"+runperiod
        # print("dataType %s" % dataType)
        # print("Data Run is %s " % (self.DataRun))
        # Analysis quantities
        self.objectClearningDr = 0.5
        if self.year == 2018:
            # Trigger

            print("Tau %s" % self.DataRun)
            if self.DataRun == "data_A":
                self.trigger = (
                    lambda e: e.HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg
                    or e.HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg
                )
            elif self.DataRun == "data_B":
                self.trigger = (
                    lambda e: e.HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg
                    or e.HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg
                )
            elif self.DataRun == "data_C":
                self.trigger = (
                    lambda e: e.HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg
                )
            elif self.DataRun == "data_D":
                self.trigger = (
                    lambda e: e.HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg
                )
            # elif self.DataRun == "mc":
            # MC
            else:
                self.trigger = (
                    lambda e: e.HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_TightID_eta2p1_Reg
                    or e.HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg
                    or e.HLT_DoubleMediumChargedIsoPFTauHPS40_Trk1_eta2p1_Reg
                    or e.HLT_DoubleMediumChargedIsoPFTauHPS40_Trk1_TightID_eta2p1_Reg
                )
            # signal
            # else: self.trigger = lambda e: e.HLT_DoubleMediumChargedIsoPFTau35_Trk1_eta2p1_Reg or e.HLT_DoubleMediumChargedIsoPFTau40_Trk1_eta2p1_Reg or e.HLT_DoubleMediumChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg or e.HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg
        # self.trigger = lambda e: e.HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg
        elif self.year == 2017:
            # Trigger
            if self.channel == "tauhtauh":
                self.trigger = (
                    lambda e: e.HLT_PFMET120_PFMHT120_IDTight
                    or e.HLT_PFMETNoMu120_PFMHTNoMu120_IDTight
                )

        elif self.year == 2016:
            # Trigger
            if self.channel == "tauhtauh":
                self.trigger = (
                    lambda e: e.HLT_PFMET120_PFMHT120_IDTight
                    or e.HLT_PFMETNoMu120_PFMHTNoMu120_IDTight
                )

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
        # if event.PV_npvs==0:
        # print("N(PV) = %s" % (event.PV_npvs))

        if not event.PV_npvs > 0:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1  # passCut+1 #passCut = 1

        # Trigger
        if not self.trigger(event):
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1  # passCut = 2

        # Taus

        # print("run:lumi:evt %s:%s:%s" % (event.run,event.luminosityBlock,self.sumNumEvt-1))
        taus = Collection(event, "Tau")
        muons = Collection(event, "Muon")
        electron = Collection(event, "Electron")
        selectedTausIdx = []
        selectedElesIdx = []
        selectedMusIdx = []

        selectTaus(event, selectedTausIdx)
        if not (
            len(selectedTausIdx) == 2
            and taus[selectedTausIdx[0]].p4().DeltaR(taus[selectedTausIdx[1]].p4())
            >= self.objectClearningDr
        ):
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1  # passCut = 3
        Tau0 = taus[selectedTausIdx[0]].p4()
        Tau1 = taus[selectedTausIdx[1]].p4()

        TauCharge = (
            event.Tau_charge[selectedTausIdx[0]] * event.Tau_charge[selectedTausIdx[1]]
        )
        if not TauCharge == -1:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1

        # mass cut on ditau if needed
        if not (Tau0 + Tau1).M() <= 100:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1

        # electrion veto
        selectEles(event, selectedElesIdx, selectedTausIdx, self.objectClearningDr)
        if not len(selectedElesIdx) == 0:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1

        # muon veto
        selectMus(event, selectedMusIdx, selectedTausIdx, self.objectClearningDr)
        if not len(selectedMusIdx) == 0:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1

        # Jets
        jets = Collection(event, "Jet")
        fatjets = Collection(event, "FatJet")
        selectedWJetsIdx = []
        selectedJetsIdx = []
        selectedTightBIdx = []
        selectedVBFJetsIdx = []

        selectFatJets(event, self.year, selectedTausIdx, selectedWJetsIdx)
        selectJets(
            event,
            self.year,
            selectedTausIdx,
            selectedWJetsIdx,
            selectedJetsIdx,
            selectedTightBIdx,
            self.objectClearningDr,
        )

        # W-Jets
        if not len(selectedWJetsIdx) >= 0:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1
        nWJets = len(selectedWJetsIdx)

        # bjet veto
        if not len(selectedTightBIdx) == 0:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1
        nBJets = len(selectedTightBIdx)

        # jetType=0 -> standard jets
        if not len(selectedJetsIdx) >= 2:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1

        Jet0 = jets[selectedJetsIdx[0]].p4()
        Jet1 = jets[selectedJetsIdx[1]].p4()

        # VBF Jets: VBF: vbfj0>0, | DY: vbfj0==0
        selectVBFJets(event, selectedJetsIdx, selectedVBFJetsIdx)
        if not len(selectedVBFJetsIdx) == 2:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1
        vbfj0 = jets[selectedVBFJetsIdx[0]].p4()
        vbfj1 = jets[selectedVBFJetsIdx[1]].p4()

        effevt(passCut, self, event)

        mjj = (vbfj0 + vbfj1).M()
        VBFJet1_Pt = vbfj0.Pt()
        VBFJet2_Pt = vbfj1.Pt()
        VBFJet1_eta = vbfj0.Eta()
        VBFJet2_eta = vbfj1.Eta()

        Jet1_Pt = Jet0.Pt()
        Jet2_Pt = Jet1.Pt()
        Jet1_Eta = Jet0.Eta()
        Jet2_Eta = Jet1.Eta()

        Dijetmass = (Jet0 + Jet1).M()

        nTaus = len(selectedTausIdx)
        Tau1Pt = Tau0.Pt()
        Tau2Pt = Tau1.Pt()
        Tau1Eta = Tau0.Eta()
        Tau2Eta = Tau1.Eta()
        RecoDiTauMass = (Tau0 + Tau1).M()
        TauDelta_Pt = Tau0.Pt() - Tau1.Pt()
        TauDeltaR = Tau0.DeltaR(Tau1)

        nJets = len(selectedJetsIdx)
        nVBF = len(selectedVBFJetsIdx)

        # MC only
        if self.isData:
            self.out.genWeight[0] = 1
        else:
            self.out.genWeight[0] = event.genWeight / abs(event.genWeight)

        # All
        # self.out.lumiWeight[0] = self.lumiWeight
        self.out.run[0] = event.run
        self.out.luminosityBlock[0] = event.luminosityBlock
        self.out.event[0] = event.event  # & 0xffffffffffffffff

        self.out.Tau1_Pt[0] = Tau1Pt
        self.out.Tau2_Pt[0] = Tau2Pt
        self.out.Tau1Eta[0] = Tau1Eta
        self.out.Tau2Eta[0] = Tau2Eta
        self.out.TauRecoMass[0] = RecoDiTauMass
        self.out.TauDeltaPt[0] = TauDelta_Pt
        self.out.TauDeltaR[0] = TauDeltaR
        self.out.nTau[0] = nTaus
        self.out.TauOSLS[0] = TauCharge
        self.out.nJet[0] = nJets
        self.out.nBJet[0] = nBJets
        self.out.nWJet[0] = nWJets
        self.out.nVBFs[0] = nVBF

        self.out.Jet1_Pt[0] = Jet1_Pt
        self.out.Jet2_Pt[0] = Jet2_Pt
        self.out.Jet1_Eta[0] = Jet1_Eta
        self.out.Jet2_Eta[0] = Jet2_Eta
        self.out.JetRecomass[0] = Dijetmass

        self.out.VBFJet1_Pt[0] = VBFJet1_Pt
        self.out.VBFJet2_Pt[0] = VBFJet2_Pt
        self.out.VBFJet1_eta[0] = VBFJet1_eta
        self.out.VBFJet2_eta[0] = VBFJet2_eta
        self.out.mjj[0] = mjj

        # Save tree
        self.out.Events.Fill()
        return True
