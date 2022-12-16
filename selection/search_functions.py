#!/usr/bin/env python3
import ROOT
import math
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection


def effevt(passCut, self, event):
    self.out.passCut[0] = passCut
    self.out.eelumiWeight[0] = self.lumiWeight
    if self.isData:
        self.out.eegenWeight[0] = 1
    else:
        self.out.eegenWeight[0] = event.genWeight / abs(event.genWeight)
    self.out.effevt.Fill()


def selectTaus(event, selectedTausIdx):
    taus = Collection(event, "Tau")
    for itau in range(event.nTau):
        if not event.Tau_pt[itau] >= 45:
            continue
        if not abs(event.Tau_eta[itau]) <= 2.1:
            continue
        if not ord(event.Tau_idDeepTau2017v2p1VSmu[itau]) >= 1:
            continue
        if not ord(event.Tau_idDeepTau2017v2p1VSe[itau]) >= 2:
            continue  # 8 = Medium
        if not ord(event.Tau_idDeepTau2017v2p1VSjet[itau]) >= 16:
            continue
        if not event.Tau_decayMode[itau] < 5:
            continue
        selectedTausIdx.append(itau)


def selectEles(event, selectedElesIdx, selectedTausIdx, objectClearningDr):
    taus = Collection(event, "Tau")
    eles = Collection(event, "Electron")
    for iele in range(event.nElectron):
        if not event.Electron_pt[iele] >= 20:
            continue
        if not abs(event.Electron_eta[iele]) <= 2.5:
            continue
        if not event.Electron_mvaFall17V2Iso_WP90[iele]:
            continue
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


# ak4 Jets
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
    for ijet in range(event.nJet):
        # Kinematic
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
        # Cleaning from tau
        isNotTau = True
        for itau in range(len(selectedTausIdx)):
            if (
                jets[ijet].p4().DeltaR(taus[selectedTausIdx[itau]].p4())
                <= objectClearningDr
            ):
                isNotTau = False
                break
        if not isNotTau:
            continue
        # Cleaning W-Jets
        isNotFatJetLep = True
        for ifatjet in range(len(selectedWJetsIdx)):
            if fatjets[selectedWJetsIdx[ifatjet]].p4().DeltaR(jets[ijet].p4()) < 0.8:
                isNotFatJetLep = False
        if not isNotFatJetLep:
            continue
        # save idx
        selectedJetsIdx.append(ijet)
        bjetEta = -1
        if year == 2016:
            bjetEta = 2.4
        if year == 2017:
            bjetEta = 2.5
        if year == 2018:
            bjetEta = 2.5
        if not abs(event.Jet_eta[ijet]) <= bjetEta:
            continue
        bjetId = 10000  # Recommendation in https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation
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
        selectedTightBIdx.append(ijet)


# Fat Jets
def selectFatJets(event, year, selectedTausIdx, selectedWJetsIdx):
    taus = Collection(event, "Tau")
    fatjets = Collection(event, "FatJet")
    for ifatjet in range(event.nFatJet):
        # Kinematic
        if not event.FatJet_pt[ifatjet] >= 200:
            continue
        if not abs(event.FatJet_eta[ifatjet]) < 2.4:
            continue  # This is the recommendation for all the fat jets (there are not reconstructed forward fat jets)
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
        # Cleaning
        isNotLep = True
        for itau in range(len(selectedTausIdx)):
            if taus[selectedTausIdx[itau]].p4().DeltaR(fatjets[ifatjet].p4()) < 0.8:
                isNotLep = False
                break
        if not isNotLep:
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
        selectedWJetsIdx.append(ifatjet)


def selectVBFJets(event, selectedJetsIdx, selectedVBFJetsIdx):
    jets = Collection(event, "Jet")
    vbfj0idx = 0
    vbfj1idx = 0
    for ijet in xrange(0, len(selectedJetsIdx) - 1):
        j0 = jets[selectedJetsIdx[ijet]].p4()
        for jjet in xrange(ijet + 1, len(selectedJetsIdx)):
            j1 = jets[selectedJetsIdx[jjet]].p4()
            jjMass = (j0 + j1).M()
            jjEta = abs(j0.Eta() - j1.Eta())
            if (
                (jjMass >= 350)
                and (jjEta >= 4.2)
                and (j0.Eta() * j1.Eta() < 0)
                and (j0.DeltaR(j1) >= 0.4)
            ):
                if vbfj0idx == 0:
                    vbfj0idx = selectedJetsIdx[ijet]
                    vbfj1idx = selectedJetsIdx[jjet]
                elif jjMass > (jets[vbfj0idx].p4() + jets[vbfj1idx].p4()).M():
                    vbfj0idx = selectedJetsIdx[ijet]
                    vbfj1idx = selectedJetsIdx[jjet]
    selectedVBFJetsIdx.append(vbfj0idx)
    selectedVBFJetsIdx.append(vbfj1idx)
