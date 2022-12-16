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
  #User inputs
  self.channel     = kwargs.get('channel')
  self.isData      = kwargs.get('dataType')=='data'
  self.year        = kwargs.get('year')
  self.maxNumEvt   = kwargs.get('maxNumEvt')
  self.prescaleEvt = kwargs.get('prescaleEvt')
  self.lumiWeight  = kwargs.get('lumiWeight')

  #Analysis quantities
  if self.year==2018:
   #Trigger
   self.trigger = lambda e: e.HLT_IsoMu24
  elif self.year==2017:
   #Trigger
   if self.channel=="mumu":
    self.trigger = lambda e: e.HLT_IsoMu24

  elif self.year==2016:
   #Trigger
   if self.channel=="mumu":
    self.trigger = lambda e: e.HLT_IsoMu24

  else:
   raise ValueError('Year must be above 2016 (included).')

  #ID

  #Corrections

  #Cut flow table

 def beginJob(self):
  print "Here is beginJob"
  #pass

 def endJob(self):
  print "Here is endJob"
  #pass

 def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
  print "Here is beginFile"
  self.sumNumEvt = 0
  self.sumgenWeight = 0
  self.out = declareVariables(inputFile)
  #pass

 def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
  print "Here is endFile"
  self.out.sumNumEvt[0] = self.sumNumEvt
  self.out.sumgenWeight[0] = self.sumgenWeight
  self.out.evtree.Fill()
  self.out.outputfile.Write()
  self.out.outputfile.Close()
  #pass

 def analyze(self, event):
  """process event, return True (go to next module) or False (fail, go to next event)"""
  #For all events
  if(self.sumNumEvt>self.maxNumEvt and self.maxNumEvt!=-1): return False
  self.sumNumEvt = self.sumNumEvt+1
  if not self.isData: self.sumgenWeight = self.sumgenWeight+(event.genWeight/abs(event.genWeight))
  if not self.sumNumEvt%self.prescaleEvt==0: return False
  passCut = 0

  #Primary vertex (loose PV selection)
  if not event.PV_npvs>0:
   effevt(passCut,self,event)
   return False
  passCut = passCut+1 #passCut = 1

  #Trigger
  if not self.trigger(event):
   effevt(passCut,self,event)
   return False
  passCut = passCut+1 #passCut = 2

  #Taus
  #print "run:lumi:evt %s:%s:%s" % (event.run,event.luminosityBlock,event.event)
  taus = Collection(event, 'Tau')
  selectedTausIdx = []
  selectMus(event,selectedTausIdx)
  if len(selectedTausIdx)!=2:
   effevt(passCut,self,event)
   return False
  passCut = passCut+1 #passCut = 3
  Tau0 = taus[selectedMusIdx[0]].p4()
  Tau1 = taus[selectedMusIdx[1]].p4()
  if not Tau0.Pt()>=30:
   effevt(passCut,self,event)
   return False
  passCut = passCut+1 #passCut = 4
  if not Tau0.Pt()-Tau1.Pt()>=30:
   effevt(passCut,self,event)
   return False
  passCut = passCut+1 #passCut = 5
  if not Tau0.DeltaR(Tau1)>=0.3:
   effevt(passCut,self,event)
   return False
  passCut = passCut+1 #passCut = 6
  if not (Tau0+Tau1).M()>=200:
   effevt(passCut,self,event)
   return False
  passCut = passCut+1 #passCut = 7
  effevt(passCut,self,event)
  #print "Tau0 idx pT |eta| ID Iso %s %s %s %s %s" % (selectedMusIdx[0],event.Muon_pt[selectedMusIdx[0]],abs(event.Muon_eta[selectedMusIdx[0]]),event.Muon_tightId[selectedMusIdx[0]],event.Muon_pfRelIso04_all[selectedMusIdx[0]])
  #print "Tau1 idx pT |eta| ID Iso %s %s %s %s %s" % (selectedMusIdx[1],event.Muon_pt[selectedMusIdx[1]],abs(event.Muon_eta[selectedMusIdx[1]]),event.Muon_tightId[selectedMusIdx[1]],event.Muon_pfRelIso04_all[selectedMusIdx[1]])
  nTaus = len(selectedTausIdx)
  Tau1Pt = tau0.Pt()
  Tau2Pt = tau1.Pt()
  Tau1Eta = tau0.Eta()
  Tau2Eta = tau1.Eta()
  RecoDiTauMass = (mu0+mu1).M()
  TauDelta_Pt = tau0.Pt()-tau1.Pt()


  #Jets
  jets = Collection(event, 'Jet')
  fatjets = Collection(event, 'FatJet')
  selectedBMJetsIdx = []
  selectedWJetsIdx = []
  selectedJetsIdx = []
  #selectVBFJetPairIdx = []
  #bjet veto
  ##jetType=0 -> standard jets, jetType=1 -> b-jets L, jetType=2 -> b-jets M, jetType=3 -> b-jets T, jetType=4 -> forward jets
  selectJets(2,event,selectedWJetsIdx,selectedMusIdx,selectedBMJetsIdx)
  if not len(selectedBMJetsIdx)==0:
   effevt(passCut,self,event)
   return False
  passCut = passCut+1
  #Fat jet
  #jetType=0 -> W-jets, jetType=1 -> top-jets
  selectFatJets(0,event,selectedMusIdx,selectedWJetsIdx)
  #if not len(selectedWJetsIdx)>=1:
  #  effevt(passCut,self,event)
  #  return False
  #passCut = passCut+1

  #ak4 jet
  selectJets(4,event,selectedWJetsIdx,selectedMusIdx,selectedJetsIdx)
  if not len(selectedJetsIdx)>=2:
   effevt(passCut,self,event)
   return False
  passCut = passCut+1
  #vbf jets
  vbfj0idx, vbfj1idx = selectVBFJetsIdx(event,selectedJetsIdx)
  #vbfj0idx, vbfj1idx = selectVBFJetPairIdx(selectedJetsIdx)
  vbfj0 = jets[vbfj0idx].p4()
  vbfj1 = jets[vbfj1idx].p4()
  """
  if not abs(vbfj0.Eta()-vbfj1.Eta())>=4.2:
   effevt(passCut,self,event)
   return False
  passCut = passCut+1
  if not vbfj0.DeltaR(vbfj1)>=0.3:
   effevt(passCut,self,event)
   return False
  passCut = passCut+1
  #if not (vbfj0+vbfj0).M()>=500:
  # effevt(passCut,self,event)
  # return False
  #passCut = passCut+1
  #if not len(selectedWJetsIdx)>=1:
  # effevt(passCut,self,event)
  # return False
  effevt(passCut,self,event) #Last cut outside the if
  """
  #Event
  nWJets = len(selectedWJetsIdx)
  nJets = len(selectedJetsIdx)
  mjj = (vbfj0+vbfj1).M()
  Jet1_Pt = vbfj0.Pt()
  Jet2_Pt = vbfj1.Pt()
  Jet1_eta = vbfj0.Eta()
  Jet2_eta = vbfj1.Eta()
  #MC only
  if self.isData:
   self.out.genWeight[0] = 1
  else:
   self.out.genWeight[0] = event.genWeight/abs(event.genWeight)
  #All
  self.out.lumiWeight[0] = self.lumiWeight
  self.out.nWJets[0] = nWJets
  self.out.nJets[0] = nJets
  self.out.Jet1_Pt[0] = Jet1_Pt
  self.out.Jet2_Pt[0] = Jet2_Pt
  self.out.Jet1_eta[0] = Jet1_eta
  self.out.Jet2_eta[0] = Jet2_eta
  self.out.mjj[0] = mjj


  print "run:lumi:evt %s:%s:%s" % (event.run,event.luminosityBlock,event.event)
  print "genWeights event.Pileup_nTrueInt %s %s" % (event.genWeight/abs(event.genWeight), event.Pileup_nTrueInt)
  print "nJets:Jet1Pt:Jet2Pt:Mjj %s:%s:%s:%s" % (nJets,Jet1_Pt,Jet2_Pt,mjj)
  print ""

  #Event
  self.out.run[0] = event.run
  self.out.luminosityBlock[0] = event.luminosityBlock
  self.out.event[0] = event.event #& 0xffffffffffffffff

  self.out.Tau1_Pt[0] = Tau1Pt
  self.out.Tau2_Pt[0] = Tau2Pt
  self.out.Tau1Eta[0] = Tau1Eta
  self.out.Tau2Eta[0] = Tau2Eta
  self.out.TauRecoMass[0] = RecoDiTauMass
  self.out.TauDeltaPt[0] = TauDelta_Pt
  self.out.nTau[0]= nTaus


  #Save tree
  self.out.Events.Fill()
  return True
