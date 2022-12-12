#!/usr/bin/env python
#Insert dataset you want to analyze
#The format is that of a list of array in python
#Eeach array has 8 entries
#0. "year": year of the dataset
#1. "datasetFlag": may stands for "SigMC", "BkgMC", the name of the dataset (e.g. "JetHT", "MET")
#2. "processName": a shortcut of the datasetName. If a dataset is an "ext", add this label and its number (e.g. DYJetsToLL_M-50_HT-100to200ext1) 
#3. "datasetName": the datasetName
#4. xSec in pb
#5. The total number of events of the dataset. To find it, use the command: dasgoclient --query="file dataset=dataset name | sum(file.nevents)". For data you should run 1 time and see the num as in data we filter the evt with the json file (to make sure you run over all evt see e.g. the tot num of files processed) 
#6. "sumgenWeight": the  sum of the genWeight of a MC dataset. Set 0 for data dataset.
#7. Label containing the analyses that need to analyze the dataset 
#Note
#1. The order of insertion of each year is first Data and then MC and must respect to avoid problems in the analysis chain
#2. The first time your run you do not know what the value of sumgenWeight is. So you need to be careful that your run over the entire dataset to get this value (see the num of files or the tot num of abs evt). Up to then, set sumgenWeight = 1 

datasets_info = [
#####
##   Year: 2018
#####
#####
##   Signal LQtop
#####
#[2017,"SigMC","ttHJetTobb_M125","/ttHJetTobb_M125_TuneCP5_13TeV_amcatnloFXFX_madspin_pythia8/RunIISummer20UL17NanoAODv9-106X_mc2017_realistic_v9-v1/NANOAODSIM",1,9.579021e+06,9.579021e+06,"LQtop"],  
[2017,"SigMC","ZprimeToBB_narrow_M-2000","/ZprimeToBB_narrow_M-2000_TuneCP5_13TeV-madgraph-pythia8/RunIISummer20UL17NanoAODv9-106X_mc2017_realistic_v9-v2/NANOAODSIM",1,297000,297000,"vbfhn"], 
#[2017,"SigMC","ZprimeToBB_narrow_M-4000","/ZprimeToBB_narrow_M-4000_TuneCP5_13TeV-madgraph-pythia8/RunIISummer20UL17NanoAODv9-106X_mc2017_realistic_v9-v2/NANOAODSIM",1,291000,291000,"LQtop"], 
]
