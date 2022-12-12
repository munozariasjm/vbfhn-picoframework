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
  self.objectClearningDr = 0.5 
  if self.year==2018:
   #Trigger 
   print "not yet"
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

#  #Trigger        
#  if not self.trigger(event):
#   effevt(passCut,self,event)
#   return False
#  passCut = passCut+1 #passCut = 2  

  print "run:lumi:evt %s:%s:%s" % (event.run,event.luminosityBlock,event.event)

  #Taus
  taus = Collection(event,'Tau')
  selectedTausIdx = []
  selectTaus(event,selectedTausIdx)
  print(len(selectedTausIdx))
  if not (len(selectedTausIdx)==2 and taus[selectedTausIdx[0]].p4().DeltaR(taus[selectedTausIdx[1]].p4())>=self.objectClearningDr): #no charge requirement atm
   effevt(passCut,self,event) 
   return False 
  passCut = passCut+1 

  #Ele veto
  selectedElesIdx = []
  selectEles(event,selectedElesIdx,selectedTausIdx,self.objectClearningDr)
  if not len(selectedElesIdx)==0:
   effevt(passCut,self,event) 
   return False 
  passCut = passCut+1 
  #Mu veto
  selectedMusIdx = []
  selectMus(event,selectedMusIdx,selectedTausIdx,self.objectClearningDr)
  if not len(selectedMusIdx)==0:
   effevt(passCut,self,event) 
   return False
  passCut = passCut+1 

  #Jets
  selectedWJetsIdx = [] 
  selectFatJets(event,year,selectedTausIdx,selectedWJetsIdx)
  selectedJetsIdx = []
  selectedTightBIdx = [] 
  selectJets(event,year,selectedTausIdx,selectedWJetsIdx,selectedJetsIdx,selectedTightBIdx,objectClearningDr)

  #Event
  self.out.run[0] = event.run
  self.out.luminosityBlock[0] = event.luminosityBlock
  self.out.event[0] = event.event #& 0xffffffffffffffff

  #Save tree
  self.out.Events.Fill() 
  return True
