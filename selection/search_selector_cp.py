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
        if self.year == 2018:
            # Trigger
            print("Tau %s" % self.DataRun)
            if self.DataRun == "data_A":
                self.trigger = (
                    lambda e: e.HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg
                    or e.HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg
                    or e.HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg
                    or e.HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg
                )
            elif self.DataRun == "data_B":
                self.trigger = (
                    lambda e: e.HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg
                    or e.HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg
                    or e.HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg
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
            else:
                self.trigger = (
                    lambda e: e.HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg
                )
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
        if not event.PV_npvs > 0:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1  # passCut+1 #passCut = 1

        # Trigger
        if not self.trigger(event):
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1  # passCut = 2

        # MET = Collection(event, 'MET')
        # selectedMETIdx = []
        # met = MET(selectedMETIdx[0]).p4()

        # MET_sumet = MET.sumEt()
        # if not MET_sumet>=30:
        #  effevt(passCut,self,event)
        #  return False
        # passCut = passCut+1
        # self.out.MET_sumet[0] = MET_sumet

        # Taus

        # print("run:lumi:evt %s:%s:%s" % (event.run,event.luminosityBlock,self.sumNumEvt-1))
        taus = Collection(event, "Tau")
        selectedTausIdx = []
        selectTaus(event, selectedTausIdx)

        if len(selectedTausIdx) != 2:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1  # passCut = 3
        Tau0 = taus[selectedTausIdx[0]].p4()
        Tau1 = taus[selectedTausIdx[1]].p4()

        if Tau0.Pt() > Tau1.Pt():
            ForwardTau = Tau0.Pt()
            smallerTauPT = Tau1.Pt()
        else:
            ForwardTau = Tau1.Pt()
            smallerTauPT = Tau0.Pt()

        # print("ForwardTau smallerPT %s %s" % (ForwardTau,smallerTauPT))
        if not Tau0.Pt() >= 60:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1  # passCut = 4

        if not Tau1.Pt() >= 60:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1  # passCut =

        TauCharge = (
            event.Tau_charge[selectedTausIdx[0]] * event.Tau_charge[selectedTausIdx[1]]
        )

        if TauCharge != -1:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1

        """
  if not Tau0.Pt()-Tau1.Pt()>=30:
   effevt(passCut,self,event)
   return False
  passCut = passCut+1 #passCut = 5
  """
        # if not Tau0.DeltaR(Tau1)>=0.3:
        # effevt(passCut,self,event)
        # return False
        # passCut = 6 #passCut = 6
        if not (Tau0 + Tau1).M() <= 100:
            effevt(passCut, self, event)
            return False
        passCut = passCut + 1  # passCut = 7

        # print("##Tau0 idx pT |eta| ID %s %s %s %s##" % (selectedTausIdx[0],event.Tau_pt[selectedTausIdx[0]],abs(event.Tau_eta[selectedTausIdx[0]]),ord(event.Tau_idDeepTau2017v2p1VSe[selectedTausIdx[0]])))
        # rint "Tau0 Tau1 Charge %s %s %s" % (event.Tau_charge[selectedTausIdx[0]],event.Tau_charge[selectedTausIdx[1]],TauCharge)
        # print("Iso %s" (ord(event.Tau_idMVAoldDM2017v2[selectedTausIdx[0]])))
        # print(ord(event.Tau_idMVAoldDM2017v2[selectedTausIdx[0]]))
        # print("Tau0 idx pT |eta| ID Iso %s %s %s %s %s" % (selectedTausIdx[0],event.Tau_pt[selectedTausIdx[0]],abs(event.Tau_eta[selectedTausIdx[0]]),event.Tau_tightId[selectedTausIdx[0]],event.Tau_pfRelIso04_all[selectedTausIdx[0]]))
        # print("Tau1 idx pT |eta| ID Iso %s %s %s %s %s" % (selectedTausIdx[1],event.Tau_pt[selectedTausIdx[1]],abs(event.Tau_eta[selectedTausIdx[1]]),event.Tau_tightId[selectedTausIdx[1]],event.Tau_pfRelIso04_all[selectedTausIdx[1]]))
        nTaus = len(selectedTausIdx)
        TauOSLS = TauCharge
        Tau1Pt = Tau0.Pt()
        Tau2Pt = Tau1.Pt()
        Tau1Eta = Tau0.Eta()
        Tau2Eta = Tau1.Eta()
        RecoDiTauMass = (Tau0 + Tau1).M()
        TauDelta_Pt = Tau0.Pt() - Tau1.Pt()

        """
  #Jets
  jets = Collection(event, 'Jet')
  fatjets = Collection(event, 'FatJet')
  selectedBMJetsIdx = []
  selectedWJetsIdx = []
  selectedJetsIdx = []
  selectVBFJetsIdx = []


  #bjet veto
  ##jetType=0 -> standard jets, jetType=1 -> b-jets L, jetType=2 -> b-jets M, jetType=3 -> b-jets T, jetType=4 -> forward jets
  selectJets(2,event,selectedWJetsIdx,selectedTausIdx,selectedBMJetsIdx)
  if not len(selectedBMJetsIdx)==0:
   effevt(passCut,self,event)
   return False
  passCut = passCut+1
  nBJets = len(selectedBMJetsIdx)


  #VBF Jets
  selectJets(4,event,selectedWJetsIdx,selectedTausIdx,selectedJetsIdx)
  if not len(selectedJetsIdx)>=2:
    effevt(passCut,self,event)
    return False
  passCut = 8
  vbfj0idx, vbfj1idx = selectVBFJetsIdx(event,selectedJetsIdx)
  vbfj0 = jets[vbfj0idx].p4()
  vbfj1 = jets[vbfj1idx].p4()
  #print(selectedJetsIdx)

  #jetType=0 -> standard jets
  selectJets(0,event,selectedWJetsIdx,selectedTausIdx,selectedJetsIdx)
  if not len(selectedJetsIdx)>=2:
    effevt(passCut,self,event)
    return False
  passCut = passCut+1


  selectJets(4,event,selectedWJetsIdx,selectedTausIdx,selectedJetsIdx)
  if not len(selectedJetsIdx)>=2:
    effevt(passCut,self,event)
    return False
  passCut = passCut+1
  vbfj0idx, vbfj1idx = selectVBFJetsIdx(event,selectedJetsIdx)
  vbfj0 = jets[vbfj0idx].p4()
  vbfj1 = jets[vbfj1idx].p4()
  """
        # Fat jet
        # jetType=0 -> W-jets, jetType=1 -> top-jets
        # selectFatJets(0,event,selectedTausIdx,selectedWJetsIdx)
        # if not len(selectedWJetsIdx)>=0:
        # effevt(passCut,self,event)
        # return False
        # passCut = passCut+1
        # HeavyNu = fatjets[selectedWJetsIdx[0]].p4() + ForwardTau
        # New variable here = ForwardTau +
        # M(#mu_{lead} + J)
        """
  if not abs(vbfj0.Eta()-vbfj1.Eta())>=4.2:
   effevt(passCut,self,event)
   return False
  passCut = 10
  if not vbfj0.DeltaR(vbfj1)>=0.3:
   effevt(passCut,self,event)
   return False
  passCut = 11
  if not (vbfj0+vbfj1).M()>=500:
   effevt(passCut,self,event)
   return False
  passCut = 12
  """

        # Event
        # nWJets = len(selectedWJetsIdx)
        # nJets = len(selectedJetsIdx)
        """
  mjj = (vbfj0+vbfj1).M()
  VBFJet1_Pt = vbfj0.Pt()
  VBFJet2_Pt = vbfj1.Pt()
  VBFJet1_eta = vbfj0.Eta()
  VBFJet2_eta = vbfj1.Eta()
  """
        # MC only
        if self.isData:
            self.out.genWeight[0] = 1
        else:
            self.out.genWeight[0] = event.genWeight / abs(event.genWeight)
        # All
        self.out.lumiWeight[0] = self.lumiWeight
        ##self.out.nWJets[0] = nWJets
        # self.out.HeavyNu[0] = HeavyNu
        """
  self.out.VBFJet1_Pt[0] = VBFJet1_Pt
  self.out.VBFJet2_Pt[0] = VBFJet2_Pt
  self.out.VBFJet1_eta[0] = VBFJet1_eta
  self.out.VBFJet2_eta[0] = VBFJet2_eta
  self.out.mjj[0] = mjj
  """

        # print("nWJets nJets  %s %s" % (nWJets,nJets))
        # print("mu0 idx pT |eta| ID Iso %s %s %s %s %s" % (selectedTausIdx[0],event.Tau_pt[selectedTausIdx[0]],abs(event.Tau_eta[selectedTausIdx[0]]),event.Tau_tightId[selectedTausIdx[0]],event.Tau_pfRelIso04_all[selectedTausIdx[0]]))
        # print("mu1 idx pT |eta| ID Iso %s %s %s %s %s" % (selectedTausIdx[1],event.Tau_pt[selectedTausIdx[1]],abs(event.Tau_eta[selectedTausIdx[1]]),event.Tau_tightId[selectedTausIdx[1]],event.Tau_pfRelIso04_all[selectedTausIdx[1]]))
        #:print("tau=2")
        # print("run:lumi:evt %s:%s:%s" % (event.run,event.luminosityBlock,event.event))
        # print("genWeights event.Pileup_nTrueInt %s %s" % (event.genWeight/abs(event.genWeight), event.Pileup_nTrueInt))
        # print("nJets:Jet1Pt:Jet2Pt:Mjj %s:%s:%s:%s" % (nJets,Jet1_Pt,Jet2_Pt,mjj))
        # print("nWJets %s" % (nWJets))
        # print("Tau OSLS %s" % (TauOSLS))
        # print("")

        # Event
        self.out.run[0] = event.run
        self.out.luminosityBlock[0] = event.luminosityBlock
        self.out.event[0] = event.event  # & 0xffffffffffffffff

        self.out.Tau1_Pt[0] = Tau1Pt
        self.out.Tau2_Pt[0] = Tau2Pt
        self.out.Tau1Eta[0] = Tau1Eta
        self.out.Tau2Eta[0] = Tau2Eta
        self.out.TauRecoMass[0] = RecoDiTauMass
        self.out.TauDeltaPt[0] = TauDelta_Pt
        self.out.nTau[0] = nTaus
        self.out.TauOSLS[0] = TauOSLS
        self.out.ForwardTaus[0] = ForwardTau
        # self.out.nBJet[0]= nBJets
        # self.out.nJet[0]=nJets
        # Save tree
        self.out.Events.Fill()
        return True
