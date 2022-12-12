#!/usr/bin/env python3
import ROOT
import math
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection


def effevt(passCut, self, event):
    passCut = passCut + 1
    self.out.passCut[0] = passCut
    self.out.eelumiWeight[0] = self.lumiWeight
    if self.isData:
        self.out.eegenWeight[0] = 1
    else:
        self.out.eegenWeight[0] = event.genWeight / abs(event.genWeight)
    self.out.effevt.Fill()


def selectTaus(event, selectedTausIdx):
    for itau in range(event.nTau):
        if not event.Tau_pt[itau] >= 20:
            continue
        if not abs(event.Tau_eta[itau]) <= 2.1:
            continue
        if not event.Tau_idDecayMode[itau] < 5:
            continue
        if not ord(event.Tau_idDeepTau2017v2p1VSjet[itau]) >= 16:
            continue  # 16 = Medium
        if not ord(event.Tau_idDeepTau2017v2p1VSe[itau]) >= 2:
            continue  # 2 = VVLoose
        if not ord(event.Tau_idDeepTau2017v2p1VSmu[itau]) >= 1:
            continue  # 1 = VLoose
        # if not abs(event.Tau_dz[itau])<=0.2: continue #not clear whether using depending on whether data/MC corrections available
        selectedTausIdx.append(itau)


def selectEles(event, selectedElesIdx, selectedTausIdx, objectClearningDr):
    taus = Collection(event, "Tau")
    eles = Collection(event, "Electron")
    for iele in range(event.nElectron):
        if not event.Electron_pt[iele] >= 20:
            continue
        if not abs(event.Electron_eta[iele]) <= 2.5:
            continue
        # if not event.Electron_cutBased[iele]>=1: continue #consider using it if mvaID not good, but not clear there are corrections for all Run2 years
        # if not event.Electron_mvaFall17V2noIso_WP90[iele]: continue #not clear whether using depending on whether data/MC corrections available for isolation
        # if not event.Electron_pfRelIso03_all[iele]>=0.1: continue #not clear whether using depending on whether data/MC corrections available for isolation
        if not event.Electron_mvaFall17V2Iso_WP90[iele]:
            continue  # consider using it if no corrections for pfRelIso03_all
        # if not abs(event.Electron_dxy[iele])<=0.045: continue #not clear whether using depending on whether data/MC corrections available
        # if not abs(event.Electron_dz[iele])<0.2: continue #not clear whether using depending on whether data/MC corrections available
        # if not event.Electron_convVeto[iele]: continue #not clear whether using depending on whether data/MC corrections available
        # if not ord(event.Electron_lostHits[iele])<=1: continue #not clear whether using depending on whether data/MC corrections available; in case, <=1 or >=1?
        isNotTau = True
        for itau in range(0, len(selectedTausIdx)):
            if (
                eles[iele].p4().DeltaR(taus[selectedTausIdx[itau]].p4())
                <= objectClearningDr
            ):
                isNotTau = False
                break
        if not isNotTau:
            continue
        selectedElesIdx.append(iele)


def selectMus(event, selectedMusIdx, selectedTausIdx, objectClearningDr):
    taus = Collection(event, "Tau")
    mus = Collection(event, "Muon")
    for imu in range(event.nMuon):
        if not event.Muon_pt[imu] >= 20:
            continue
        if not abs(event.Muon_eta[imu]) <= 2.4:
            continue
        # if not event.Muon_looseId[imu]: continue
        if not event.Muon_mediumId[imu]:
            continue
        if not ord(event.Muon_pfIsoId[imu]) >= 2:
            continue
        isNotTau = True
        for itau in range(0, len(selectedTausIdx)):
            if (
                mus[imu].p4().DeltaR(taus[selectedTausIdx[itau]].p4())
                <= objectClearningDr
            ):
                isNotTau = False
                break
        if not isNotTau:
            continue
        selectedMusIdx.append(imu)


def selectFatJets(event, year, selectedTausIdx, selectedWJetsIdx):
    taus = Collection(event, "Tau")
    fatjets = Collection(event, "FatJet")
    for ifatjet in range(event.nFatJet):
        # kinematic
        if not event.FatJet_pt >= 200:
            continue  # As we use particleNet, this seems the minimal pT above which SF are measured (see https://twiki.cern.ch/twiki/bin/view/CMS/ParticleNetTopWSFs)
        if not abs(event.FatJet_eta[ifatjet]) < 2.4:
            continue
        # ID
        jetId = 10000  # Recommendation in https://twiki.cern.ch/twiki/bin/view/CMS/JetID#Recommendations_for_13_TeV_data and https://twiki.cern.ch/twiki/bin/view/CMS/JetID13TeVUL ("Please note: For AK8 jets, the corresponding (CHS or PUPPI) AK4 jet ID should be used.")
        if year == 2016 or year == 1016:
            jetId = 3  # tight ID
        if year == 2017:
            jetId = 2  # tight ID
        if year == 2018:
            jetId = 2  # tight ID
        if not event.FatJet_jetId[ifatjet] >= jetId:
            continue
        # cleaning
        isNotTau = True
        for itau in range(0, len(selectedTausIdx)):
            if taus[selectedTausIdx[itau]].p4().DeltaR(fatjets[ifatjet].p4()) < 0.8:
                isNotTau = False
                break
        if not isNotTau:
            continue
        # W tagged jet
        pNetId = 10000  # Recommendation in https://twiki.cern.ch/twiki/bin/view/CMS/ParticleNetTopWSFs
        if year == 1016:
            pNetId = 0.94  # Medium ID
        if year == 2016:
            pNetId = 0.93  # Medium ID
        if year == 2017:
            pNetId = 0.94  # Medium ID
        if year == 2018:
            pNetId = 0.94  # Medium ID
        if not event.FatJet_particleNet_WvsQCD[ifatjet] >= pNetId:
            continue
        # save idx
        selectedWJetsIdx.append(ifatjet)
        # Old W/Top tagging algorithm
        # tau21Cut = 1
        # if year==2016: tau21Cut=0.35
        # if year==2017: tau21Cut=0.45
        # if year==2018: tau21Cut=0.35
        # if not (65<FatJet_msoftdrop_Wtag and FatJet_msoftdrop_Wtag<105 and event.FatJet_tau2[ifatjet]/event.FatJet_tau1[ifatjet]<tau21Cut): continue
        # selectedWJetsIdx.append(ifatjet)
        # Top tagged jet
        # elif (FatJet_pt>=400 and 105<FatJet_msoftdrop and FatJet_msoftdrop<220 and event.FatJet_tau3[ifatjet]/event.FatJet_tau2[ifatjet]<0.81):
        # fatjet = ROOT.TLorentzVector()
        # fatjet.SetPtEtaPhiM(FatJet_pt, event.FatJet_eta[ifatjet], event.FatJet_phi[ifatjet], FatJet_msoftdrop)
        # selectedTopJetsIdx.append(ifatjet)
        # selectedTopJets.append(fatjet)


def selectJets(
    event,
    year,
    selectedTausIdx,
    selectedWJetsIdx,
    selectedJetsIdx,
    selectedTightBIdx,
    objectClearningDr,
):
    taus = Collection(event, "Tau")
    fatjets = Collection(event, "FatJet")
    jets = Collection(event, "Jet")
    for ijet in range(0, event.nJet):
        # print "jets idx pT eta phi ID %s %s %s %s %s" % (ijet,event.Jet_pt[ijet],abs(event.Jet_eta[ijet]),event.Jet_phi[ijet],event.Jet_jetId[ijet])
        # kinematic
        if not event.Jet_pt[ijet] >= 20:
            continue
        if not abs(event.Jet_eta[ijet]) <= 5.0:
            continue
        # ID
        jetId = 10000  # Recommendation in https://twiki.cern.ch/twiki/bin/view/CMS/JetID#Recommendations_for_13_TeV_data and https://twiki.cern.ch/twiki/bin/view/CMS/JetID13TeVUL ("Please note: For AK8 jets, the corresponding (CHS or PUPPI) AK4 jet ID should be used.")
        if year == 2016 or year == 1016:
            jetId = 3  # tight ID
        if year == 2017:
            jetId = 2  # tight ID
        if year == 2018:
            jetId = 2  # tight ID
        if not event.Jet_jetId[ijet] >= jetId:
            continue
        # cleaning
        isNotTau = True
        for itau in range(0, len(selectedTausIdx)):
            if taus[selectedTausIdx[itau]].p4().DeltaR(jets[ijet].p4()) < 0.5:
                isNotTau = False
                break
        if not isNotTau:
            continue
        isNotFatJetLep = True
        for ifatjet in range(len(selectedWJetsIdx)):
            if fatjets[selectedWJetsIdx[ifatjet]].p4().DeltaR(jets[ijet].p4()) < 0.8:
                isNotFatJetLep = False
        if not isNotFatJetLep:
            continue
        # save idx
        selectedJetsIdx.append(ijet)
        # b-jet
        bjetEta = -1
        if year == 2016:
            bjetEta = 2.4
        if year == 2017:
            bjetEta = 2.5
        if year == 2018:
            bjetEta = 2.5
        if not abs(event.Jet_eta[ijet]) <= bjetEta:
            continue
        # bjetId = 10000  # Recommendation in https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation
        # tight working point, as this is for a veto, as done in EXO-21-015
        if year == 1016:
            jetId = 0.6502  # L,M,T: 0.0508,0.2598,0.6502 see https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation106XUL16preVFP
        if year == 2016:
            jetId = 0.6377  # L,M,T: 0.0480,0.2489,0.6377 see https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation106XUL16postVFP
        if year == 2017:
            jetId = 0.7476  # L,M,T: 0.0532,0.3040,0.7476 see https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation106XUL17
        if year == 2018:
            jetId = 0.7100  # L,M,T: 0.0490,0.2783,0.7100 see https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation106XUL18
        if not event.Jet_btagDeepFlavB[ijet] >= jetId:
            continue
        # save b idx
        selectedTightBIdx.append(ijet)
