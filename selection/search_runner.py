#!/usr/bin/env python3
import os
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
    "-c",
    "--channel",
    dest="channel",
    action="store",
    choices=["mumu", "ee"],
    type=str,
    default="mumu",
)
parser.add_argument(
    "-dt",
    "--dataType",
    dest="dataType",
    action="store",
    choices=["data", "mc"],
    default="mc",
)
parser.add_argument(
    "-y",
    "--year",
    dest="year",
    action="store",
    choices=[1016, 2016, 2017, 2018],
    type=int,
    default=2017,
)
parser.add_argument(
    "-ne", "--maxNumEvt", dest="maxNumEvt", action="store", type=int, default=-1
)
parser.add_argument(
    "-pe", "--prescaleEvt", dest="prescaleEvt", action="store", type=int, default=1
)
parser.add_argument(
    "-lw", "--lumiWeight", dest="lumiWeight", action="store", type=float, default=1
)
parser.add_argument(
    "-if", "--inputFile", dest="inputFile", action="store", type=str, default="None"
)
args = parser.parse_args()
process = args.process
channel = args.channel
dataType = args.dataType
year = args.year
maxNumEvt = args.maxNumEvt
prescaleEvt = args.prescaleEvt
lumiWeight = args.lumiWeight
inputFile = args.inputFile
kwargs = {
    "channel": channel,
    "dataType": dataType,
    "year": year,
    "maxNumEvt": maxNumEvt,  #  It is the maximum number of events you want to analyze. -1 means all entries from the input file.
    "prescaleEvt": prescaleEvt,  # It allows to analyze 1 event every N. 1 means analyze all events.
    "lumiWeight": lumiWeight,
}

# Modules
from search_selector import *

module2run = lambda: Producer(**kwargs)

# Input files
if inputFile is "None":
    if dataType == "data":
        if year == 2017:
            infiles = [
                "root://cms-xrd-global.cern.ch//store/data/Run2017B/Tau/NANOAOD/31Mar2018-v1/10000/04463969-D044-E811-8DC1-0242AC130002.root"
            ]
        elif year == 2016:
            infiles = [
                "root://cms-xrd-global.cern.ch//store/group/phys_tau/ProdNanoAODv4Priv/16dec18/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4Priv-from_102X_upgrade2018_realistic_v15_ver2/181216_125027/0000/myNanoRunMc2018_NANO_75.root"
            ]
        else:
            raise ValueError('"year" must be above 2016 (included).')

    elif dataType == "mc":
        if year == 2017:
            infiles = [
                #'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAOD/VBF_WprimeToWZ_narrow_M-4500_TuneCP5_13TeV-madgraph/NANOAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/30000/B0B2DF44-6834-E911-97AF-AC1F6B23C834.root', #32000 used for first synch with Brandon
                #'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAOD/DYJetsToLL_M-50_HT-2500toInf_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/110000/D8DDA30A-49AE-E811-A08B-0CC47A5FBDC1.root' #47415
                #'/afs/cern.ch/user/f/fromeo/public/4Brandon/D8DDA30A-49AE-E811-A08B-0CC47A5FBDC1.root'
                #'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16NanoAODv5/DYJetsToLL_M-50_HT-600to800_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/120000/92268EC5-122A-0648-82C5-41296A10FD29.root'
                "/eos/cms/store/group/phys_b2g/azp/hn/simulation/RunIISummer20UL18/NanoAODv2/WWFusion/coupling1/mass10000/NanoAODv2_0.root"
            ]
        elif year == 2016:
            infiles = [
                "root://cms-xrd-global.cern.ch//store/group/phys_tau/ProdNanoAODv4Priv/16dec18/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4Priv-from_102X_upgrade2018_realistic_v15_ver1/181216_125011/0000/myNanoRunMc2018_NANO_101.root"
            ]
        else:
            raise ValueError('"year" must be above 2016 (included).')

    else:
        raise ValueError('"dataType" must be "data" or "mc".')
else:
    infiles = []
    infiles.append(inputFile)

# JSON files for data
# 201X https://twiki.cern.ch/twiki/bin/view/CMS/PdmV201XAnalysis
# /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/ReReco/
# jsonfile = "./PicoFramework/TreeProducer/data/corrections/json/"
jsonfile = os.environ["CMSSW_BASE"] + "/src/PicoFramework/TreeProducer/data/json/"
# if year==2018:
# elif year==2017:
jsonfile = jsonfile + "Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON_v1.txt"
# elif year==2016:
# else:
# raise ValueError('"year" must be above 2016 (included).')

# Run
# All options
# PostProcessor(outputDir,inputFiles,cut=None,branchsel=None,modules=[],compression="LZMA:9",friend=False,postfix=None,jsonInput=None,noOut=False,justcount=False,provenance=False,haddFileName=None,fwkJobReport=False,histFileName=None,histDirName=None,outputbranchsel=None)
if dataType == "data":
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
elif dataType == "mc":
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
    raise ValueError('"dataType" must be "data" or "mc".')
p.run()
print("DONE")
