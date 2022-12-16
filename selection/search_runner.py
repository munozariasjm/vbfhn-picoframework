#!/usr/bin/env python
import os, sys
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import (
    PostProcessor,
)
from argparse import ArgumentParser

# This takes care of converting the input files from CRAB. It is the reason for which you need the file PSet.py also in the python directory.
from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import (
    inputFiles,
    runsAndLumis,
)

# User inputs
parser = ArgumentParser()
parser.add_argument(
    "-p",
    "--process",
    dest="process",
    action="store",
    choices=["local", "queue", "crab"],
    default="local",
)
parser.add_argument(
    "-a", "--analysis", dest="analysis", action="store", type=str, default="LQtop"
)  # Name of the analysis (e.g. VBFHN)
parser.add_argument(
    "-y",
    "--year",
    dest="year",
    action="store",
    choices=[2016, 2017, 2018],
    type=int,
    default=2016,
)
parser.add_argument(
    "-dt",
    "--dataType",
    dest="dataType",
    action="store",
    choices=[
        "data_A",
        "data_B",
        "data_C",
        "data_D",
        "data_E",
        "data_F",
        "data_G",
        "data_H",
        "mc",
        "SigMC",
    ],
    default="mc",
)
parser.add_argument(
    "-c",
    "--channel",
    dest="channel",
    action="store",
    choices=["tauhtauh", "mutau", "eletau", "muele", "mumu", "ee"],
    type=str,
    default="tauhtauh",
)
parser.add_argument(
    "-pn",
    "--processName",
    dest="processName",
    action="store",
    type=str,
    default="SingleVectorLQ_InclusiveDecay_M-1100",
)
parser.add_argument(
    "-lw", "--lumiWeight", dest="lumiWeight", action="store", type=float, default=1
)
parser.add_argument(
    "-bt",
    "--btagEff",
    dest="btagEff",
    action="store",
    choices=[True, False],
    type=bool,
    default=False,
)
parser.add_argument(
    "-if", "--inputFile", dest="inputFile", action="store", type=str, default="None"
)
parser.add_argument(
    "-ne", "--maxNumEvt", dest="maxNumEvt", action="store", type=int, default=-1
)
parser.add_argument(
    "-pe", "--prescaleEvt", dest="prescaleEvt", action="store", type=int, default=1
)
args = parser.parse_args()
process = args.process
analysis = args.analysis
year = args.year
dataType = args.dataType
channel = args.channel
processName = args.processName
lumiWeight = args.lumiWeight
btagEff = args.btagEff
inputFile = args.inputFile
maxNumEvt = args.maxNumEvt
prescaleEvt = args.prescaleEvt
kwargs = {
    "analysis": analysis,
    "year": year,
    "dataType": dataType,
    "channel": channel,
    "processName": processName,
    "lumiWeight": lumiWeight,
    "btagEff": btagEff,
    "maxNumEvt": maxNumEvt,  # It is the maximum number of events you want to analyze. -1 means all entries from the input file.
    "prescaleEvt": prescaleEvt,  # It allows to analyze 1 event every N. 1 means analyze all events.
}

# Modules
from search_selector import *

# from PicoFramework.TreeProducer.LQtop_Selection import *
module2run = lambda: Producer(**kwargs)

# Input files
if inputFile is "None":
    if "data" in dataType:
        if year == 2018:
            infiles = [
                "root://cms-xrd-global.cern.ch//store/data/Run2018C/MET/NANOAOD/Nano14Dec2018-v1/00000/0FBE8061-3708-5E4D-BD55-6B4838224998.root"
            ]
        elif year == 2017:
            infiles = [
                "root://cms-xrd-global.cern.ch//store/data/Run2017B/MET/NANOAOD/Nano14Dec2018-v1/90000/F8D89621-0055-3040-AA0A-387519E967CB.root"
            ]
        elif year == 2016:
            infiles = [
                "root://cms-xrd-global.cern.ch//store/group/phys_tau/ProdNanoAODv4Priv/16dec18/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4Priv-from_102X_upgrade2018_realistic_v15_ver2/181216_125027/0000/myNanoRunMc2018_NANO_75.root"
            ]
        else:
            raise ValueError('"year" must be above 2016 (included).')

    elif "mc" in dataType:
        if year == 2018:
            infiles = [
                "root://cms-xrd-global.cern.ch//store/mc/RunIISummer20UL18NanoAODv9/QCD_HT200to300_TuneCP5_PSWeights_13TeV-madgraph-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v1/270000/9072FB34-9A52-0A40-8234-EA18C6C7FC48.root",
                "root://cms-xrd-global.cern.ch//store/mc/RunIISummer20UL18NanoAODv9/QCD_HT200to300_TuneCP5_PSWeights_13TeV-madgraph-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v1/270000/EB1F0731-1F7D-F040-8789-9AB84AA8D295.root",
                "root://cms-xrd-global.cern.ch//store/mc/RunIISummer20UL18NanoAODv9/QCD_HT200to300_TuneCP5_PSWeights_13TeV-madgraph-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v1/270000/B1F54F04-E207-194B-BBE0-54F4E6C50422.root",
                "root://cms-xrd-global.cern.ch//store/mc/RunIISummer20UL18NanoAODv9/QCD_HT200to300_TuneCP5_PSWeights_13TeV-madgraph-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v1/270000/BC1A6A8A-8BD8-2D4E-B10C-BF127C15CB3C.root",
                "root://cms-xrd-global.cern.ch//store/mc/RunIISummer20UL18NanoAODv9/QCD_HT200to300_TuneCP5_PSWeights_13TeV-madgraph-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v1/2530000/44D050EE-57B7-A745-90B8-4A395630A200.root",
                "root://cms-xrd-global.cern.ch//store/mc/RunIISummer20UL18NanoAODv9/QCD_HT200to300_TuneCP5_PSWeights_13TeV-madgraph-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v1/2530000/8698468E-1597-EC46-95C4-25441396D7AA.root",
                "root://cms-xrd-global.cern.ch//store/mc/RunIISummer20UL18NanoAODv9/QCD_HT200to300_TuneCP5_PSWeights_13TeV-madgraph-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v1/2520000/E6CF6276-F472-4946-8775-28DE09AC06C0.root",
                "root://cms-xrd-global.cern.ch//store/mc/RunIISummer20UL18NanoAODv9/QCD_HT200to300_TuneCP5_PSWeights_13TeV-madgraph-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v1/2520000/39F253DF-80F4-5D47-B9DE-0693F61C2639.root",
                "root://cms-xrd-global.cern.ch//store/mc/RunIISummer20UL18NanoAODv9/QCD_HT200to300_TuneCP5_PSWeights_13TeV-madgraph-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v1/2520000/CF7F3432-35DE-9747-906B-6CBFA8A59AE4.root",
                "root://cms-xrd-global.cern.ch//store/mc/RunIISummer20UL18NanoAODv9/QCD_HT200to300_TuneCP5_PSWeights_13TeV-madgraph-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v1/2520000/38F8E390-3747-3A4D-AF57-6AA65FA92F92.root"
                #'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/PairVectorLQ_InclusiveDecay_M-1000_TuneCP5_13TeV-madgraph-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/40000/BEB9C1B1-65BB-4044-B548-35F4EF24530F.root' #700000 evt
            ]
        elif year == 2016:
            # infiles = ['root://cms-xrd-global.cern.ch//store/group/phys_tau/ProdNanoAODv4Priv/16dec18/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4Priv-from_102X_upgrade2018_realistic_v15_ver1/181216_125011/0000/myNanoRunMc2018_NANO_101.root'
            infiles = [
                "root://cms-xrd-global.cern.ch//store/mc/RunIISummer16NanoAODv6/SingleVectorLQ_InclusiveDecay_M-1100_TuneCP2_13TeV-madgraph-pythia8/NANOAODSIM/PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/100000/67BB61E9-2694-0648-9F41-08A55AC7296B.root",
                "root://cms-xrd-global.cern.ch//store/mc/RunIISummer16NanoAODv6/SingleVectorLQ_InclusiveDecay_M-1100_TuneCP2_13TeV-madgraph-pythia8/NANOAODSIM/PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/100000/E710F569-3E5F-6D4E-9A9C-A48D47DB922C.root",
                "root://cms-xrd-global.cern.ch//store/mc/RunIISummer16NanoAODv6/SingleVectorLQ_InclusiveDecay_M-1100_TuneCP2_13TeV-madgraph-pythia8/NANOAODSIM/PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/270000/4EBBF6A7-E449-6F46-A301-63B1B8407E88.root",
            ]
        else:
            raise ValueError('"year" must be above 2016 (included).')

    else:
        raise ValueError('"dataType" must be "dataX" or "mc".')
else:
    infiles = []
    infiles.append(inputFile)

# JSON files for data
# 201X https://twiki.cern.ch/twiki/bin/view/CMS/PdmV201XAnalysis
# /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/CollisionsX/13TeV/ReReco/
jsonfile = os.environ["CMSSW_BASE"] + "/src/vbfhn-picoframework/TreeProducer/data/json/"
if year == 2018:
    jsonfile = jsonfile + "Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt"
elif year == 2017:
    jsonfile = (
        jsonfile + "Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON_v1.txt"
    )
elif year == 2016:
    jsonfile = (
        jsonfile + "Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt"
    )
# else:
# raise ValueError('"year" must be above 2016 (included).')

# Run
# All options
# PostProcessor(outputDir,inputFiles,cut=None,branchsel=None,modules=[],compression="LZMA:9",friend=False,postfix=None,jsonInput=None,noOut=False,justcount=False,provenance=False,haddFileName=None,fwkJobReport=False,histFileName=None,histDirName=None,outputbranchsel=None)
if "data" in dataType:
    if process == "local":
        p = PostProcessor(
            outputDir=".", noOut=True, modules=[module2run()], inputFiles=infiles
        )  # ,jsonInput=jsonfile) #No need jsonInput locally (it takes sometime to prefilter evt)
    if process == "queue":
        p = PostProcessor(
            outputDir=".",
            noOut=True,
            modules=[module2run()],
            inputFiles=infiles,
            jsonInput=jsonfile,
        )
    if process == "crab":
        p = PostProcessor(
            outputDir=".",
            noOut=True,
            modules=[module2run()],
            inputFiles=inputFiles(),
            jsonInput=jsonfile,
            fwkJobReport=True,
        )
elif "mc" in dataType:
    if process == "local":
        p = PostProcessor(
            outputDir=".", noOut=True, modules=[module2run()], inputFiles=infiles
        )
    if process == "queue":
        p = PostProcessor(
            outputDir=".", noOut=True, modules=[module2run()], inputFiles=infiles
        )
    if process == "crab":
        p = PostProcessor(
            outputDir=".",
            noOut=True,
            modules=[module2run()],
            inputFiles=inputFiles(),
            fwkJobReport=True,
        )
elif "SigMC" in dataType:
    if process == "local":
        p = PostProcessor(
            outputDir=".", noOut=True, modules=[module2run()], inputFiles=infiles
        )
    if process == "queue":
        p = PostProcessor(
            outputDir=".", noOut=True, modules=[module2run()], inputFiles=infiles
        )
    if process == "crab":
        p = PostProcessor(
            outputDir=".",
            noOut=True,
            modules=[module2run()],
            inputFiles=inputFiles(),
            fwkJobReport=True,
        )
else:
    raise ValueError('"dataType" must be "data", "mc", or "SigMC".')
p.run()
print("DONE")
