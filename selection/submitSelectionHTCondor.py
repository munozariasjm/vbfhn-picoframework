#!/usr/bin/env python2
#Notes
#1. the part "/tmp/x509up_u30997" works only on fromeo laptop.
# If you use this script, make sure it update it to work on your machine.
#Issus with merging
#1.
# Error in <TFile::ReadBuffer>: error reading all requested bytes from file
# /eos/cms/store/group/phys_exotica/LQtop/FullRun2_30Apr/2017/mergedFiles/TTZToQQ.root,
# got 0 of 300
#Error in <TFile::Init>: /eos/cms/store/group/phys_exotica/LQtop/FullRun2_30Apr/2017/mergedFiles/TTZToQQ.root failed to read the file type data.
#2.
#2018 MET_A /eos/cms/store/group/phys_exotica/LQtop/TrigEffMHT/2018/MET_A/884DAEBD-77D0-234E-BBEB-61CFD2AFB06C_Skim.root does not have hltMu50 variables and it creates a warning when merging with other tree that have it
#3.
#If you get the error HTCondor ERROR: The 'output' takes exactly one argument (output/, delete the folder created in ./analysis/task which likely have .txt files that are recalled when submitting the .cfg file to condor
#Run me with python -u (if you go in background)
import os, sys, subprocess
from commands import getoutput
#Needed to submit the task
passwd = os.popen('cat /afs/cern.ch/user/b/bsoubasi/private/vomsproxy').read().strip()
#The dataset information
path_fw = os.environ['CMSSW_BASE']+"/src/vbfhn-picoframework/"
path_utils = path_fw+"utils/"
sys.path.append(path_utils)
sys.path.append(path_utils+'datasets_info.py')
from datasets_info import *
#Missing files in years
missing_files = []
missing_files.append("2018_DYJetsToLL_M-50_HT-1200To2500")
missing_files.append("2018_DYJetsToLL_M-50_HT-2500ToInf")
missing_files.append("2018_ZJetsToNuNu_HT-400To600")
missing_files.append("2018_WZTo1L1Nu2Q")
missing_files.append("2018_tZq_Zhad_Wlept_4f_ckm_NLO")
missing_files.append("2016_tZq_Zhad_Wlept_4f_ckm_NLO")
year_from_which_copy_missing_files = "2017"
#User input
from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument('-lp',   '--lnfPath',     dest='lnfPath',     action='store', type=str, default='/home-b/bsoubasi/Output/') #/cms/store/user/fromeo/')
parser.add_argument('-p',    '--process',     dest='process',     action='store', choices=['local','queue','crab'], default='queue')
parser.add_argument('-a',    '--analysis',    dest='analysis',    action='store', type=str, default='vbfhn') #Name of the analysis (e.g. VBFHN, LQtop, ...)
parser.add_argument('-t',    '--task',        dest='task',        action='store', type=str, default='test') #Name of the task (e.g. Test, SignalRegion, ControlRegion, FullAnalysis, ...)
parser.add_argument('-ys',   '--years',       dest='years',       action='store', type=str, default='2016_2017_2018') #The years you want to process (separated by _!)
parser.add_argument('-dfd',  '--datasetFlagData', dest='datasetFlagData', action='store', type=str, default='MET') #See datasets_info[d][1] in datasets_info.py. "All" stands for all he cases.
parser.add_argument('-dfmc', '--datasetFlagMC',   dest='datasetFlagMC',   action='store', type=str, default='All') #"All" for all he cases "SigMC" for signal samples "BkgMC" for SM samples "None" no samples
parser.add_argument('-c',    '--channel',     dest='channel',     action='store', choices=['tauhtauh','mutau','eletau','muele','mumu','ee'], type=str,   default='tauhtauh')
parser.add_argument('-lw',   '--lumiWeight',  dest='lumiWeight',  action='store', type=float, default=1)
parser.add_argument('-bt',   '--btagEff',     dest='btagEff',     action='store', choices=[True,False], type=bool, default=False)
parser.add_argument('-mo',   '--mergeOnly',   dest='mergeOnly',   action='store', choices=[True,False], type=bool, default=False)
parser.add_argument('-etm',  '--evtThMerge',  dest='evtThMerge',  action='store', type=float, default=0.975)
parser.add_argument('-qh',   '--queueHours',  dest='queueHours',  action='store', type=int, default=24)
parser.add_argument('-i',    '--iterations',  dest='iterations',  action='store', type=int, default='1')
parser.add_argument('-ts',   '--timeSleep',   dest='timeSleep',   action='store', type=str, default='1s')
#It means you run for a maximum time of iterations*timeSleep
args = parser.parse_args()
lnfPath     = args.lnfPath
process     = args.process
analysis    = args.analysis
task        = args.task
years       = args.years
datasetFlagData = args.datasetFlagData
datasetFlagMC   = args.datasetFlagMC
channel     = args.channel
lumiWeight  = args.lumiWeight
btagEff     = args.btagEff
mergeOnly   = args.mergeOnly
evtThMerge  = args.evtThMerge
queueHours  = args.queueHours
iterations  = args.iterations
timeSleep   = args.timeSleep

def main():
 #Create report files
 completeDatasetName = '%sselection/%s_%s_completeDatasets.txt' % (path_fw,task,years)
 if os.path.isfile(completeDatasetName): os.system("rm %s" % (completeDatasetName))
 completeDataset = file(completeDatasetName,"a+")
 incompleteDatasetName = '%sselection/%s_%s_incompleteDatasets.txt' % (path_fw,task,years)
 if os.path.isfile(incompleteDatasetName): os.system("rm %s" % (incompleteDatasetName))
 incompleteDataset = file(incompleteDatasetName,"a+")
 nullDatasetName = '%sselection/%s_%s_nullDatasets.txt' % (path_fw,task,years)
 if os.path.isfile(nullDatasetName): os.system("rm %s" % (nullDatasetName))
 nullDataset = file(nullDatasetName,"a+")
 #Create and enter the folder for the analysis/task
 if not os.path.exists(analysis): os.makedirs(analysis)
 os.chdir(analysis)
 if not os.path.exists(task): os.makedirs(task)
 os.chdir(task)
 path_at = (os.popen("pwd").read()).strip() #.strip() removes empty characters
 if not os.path.exists("failedFiles"): os.makedirs("failedFiles")
 if not os.path.exists("/eos"+lnfPath+analysis): os.makedirs("/eos"+lnfPath+analysis)
 if not os.path.exists("/eos"+lnfPath+analysis+"/"+task): os.makedirs("/eos"+lnfPath+analysis+"/"+task)
 #Start processing
 num_datasets_of_interest = 0
 already_merged = 0
 merged_datasetnames = []
 finished_datasetnames = []
 incomplete_datasets = 0
 null_datasets = 0
 keep_checking_count = 0
 while(keep_checking_count<iterations):
  keep_checking_count = keep_checking_count+1
  print "Iterations %s " % (keep_checking_count)
  #You must initialize the proxy (and apparently more than just the first time when you run on the queue)
  os.system('echo %s | voms-proxy-init --valid 192:00 -voms cms -rfc' % (passwd)) #192 means keep the credentials valid for 192h
  os.system("cp /tmp/x509up_u106282 %sselection" % (path_fw))
  #Loop over all datasets of interest
  for d in range(0,len(datasets_info)):
   os.chdir(path_at) #For every dataset come back to the folder analysis/task
   #Choose analysis
   if not analysis in datasets_info[d][7]: continue
   #Choose year
   year = str(datasets_info[d][0])
   if not year in years: continue
   if not os.path.exists(year): os.makedirs(year)
   os.chdir(year)
   if not os.path.exists("/eos"+lnfPath+analysis+"/"+task+"/"+year): os.makedirs("/eos"+lnfPath+analysis+"/"+task+"/"+year)
   #Check dataset has not already finished
   processName = datasets_info[d][2]
   if year+"_"+processName in finished_datasetnames: continue
   #Get some more info
   outputPathProcessName = "/eos"+lnfPath+analysis+"/"+task+"/"+year+"/"+processName
   outputPathMergedFiles = "/eos"+lnfPath+analysis+"/"+task+"/"+year+"/"+"mergedFiles"
   datasetName = datasets_info[d][3]
   if "NANOAODSIM" in datasetName: dataType="mc"
   elif "NANOAOD" in datasetName:
    runperiod = processName.replace(datasets_info[d][1],'')
    dataType="data"
    #dataType="data"+runperiod
   else: raise ValueError('Which dataType are you using?')
   #Choose datasetFlag
   if "data" in dataType and not (datasetFlagData==datasets_info[d][1] or datasetFlagData=="All"): continue
   if "mc"   in dataType and not (datasetFlagMC==datasets_info[d][1] or datasetFlagMC=="All"): continue
   print '%s %s' % (year,processName)
   if mergeOnly and keep_checking_count==1: num_datasets_of_interest = num_datasets_of_interest+1
   if os.path.isfile(outputPathMergedFiles+"/"+processName+".root"):
    if not year+"_"+processName in merged_datasetnames: merged_datasetnames.append(year+"_"+processName)
    if mergeOnly: already_merged = already_merged+1 #Useful if you rerun this script (as finished_datasetnames is reinizialized)
    continue #This can happen if you have more iterations within the same run
   fileList = getDatasetFileList(year,processName)
   #Submit
   if not mergeOnly and keep_checking_count==1: #First iteration is for submission (unless "mergeOnly" is True)
    num_datasets_of_interest = num_datasets_of_interest+1
    #Create needed folder
    if not os.path.exists(processName): os.makedirs(processName)
    os.chdir(processName)
    if not os.path.exists("error"): os.makedirs("error") #Do it here to avoid conflicts with !(*cfg) in prepareSubDataset
    if not os.path.exists("log"): os.makedirs("log")
    if not os.path.exists("output"): os.makedirs("output")
    if not os.path.exists(outputPathProcessName): os.makedirs(outputPathProcessName)
    lumiWeight = getlumiWeight(dataType,year,datasets_info[d][4],datasets_info[d][6])
    #Get dataset's rootfiles
    #fileList = getDatasetFileList(year,processName)
    #Prepare 1 job for each dataset file
    for f in fileList:
     head,tail = os.path.split(f)
     fileName = tail.replace('.root','')
     #prepareSubFile(fileName,year,processName)
     prepareSHFile(f,fileName,year,dataType,processName,lumiWeight)
     #os.system("condor_submit %s.cfg" % (fileName))
    #Prepare and submit 1 task per dataset
    prepareSubDataset(year,processName)
    os.system("condor_submit %s.cfg" % (processName))
    if "data" in dataType: os.system("condor_submit %s.cfg" % (processName)) #TRY: submitting 2 times to increase the chances to have 100% success of the jobs (need to make sure no conflicts are created with same produced files)
   #Check/Merge
   else:
    if not os.path.exists(outputPathMergedFiles): os.makedirs(outputPathMergedFiles)
    #keephadd if at least X% of events have been parsed for MC samples or 100% of events is parsed for data
    #1. Consider only files that have a size > 1000 byte, meaning they are finished
    rootFilesListFile = file(processName+".txt","w")
    for subdir, dir, files in os.walk('%s' % (outputPathProcessName)):
     for fl in files:
      pathFile = outputPathProcessName+"/"+fl
      if int(os.stat(pathFile).st_size)>1000: print >> rootFilesListFile, "%s/%s" % (outputPathProcessName,fl)
    rootFilesListFile.close()
    rootFilesListFile = file(processName+".txt","r")
    #2. Check files, sumNumEvt, sumgenWeight
    #Files
    numReadyRootFiles = int(getoutput('cat %s.txt | grep root | wc -l' % (processName)))
    print "%s we are in %s" % (processName,(os.popen("pwd").read()).strip())
    path_null = (os.popen("pwd").read()).strip()
    if not numReadyRootFiles>0:
     if keep_checking_count==iterations:
       #os.system("mail -s \"No files produced for %s %s\" brandon.j.soubasis@vanderbilt.edu < /dev/null" % (year,processName)) #If this happens there is a problem
       null_datasets = null_datasets+1
       print >> nullDataset, "%s %s" % (year,processName)
       os.chdir(path_null+'/'+processName) #Need to be in this folder to properly resubmit on condor
       #os.system("condor_submit %s.cfg" % (processName)) #TRY to resubmit on condorHT (maybe something got wrong before)
                                                          #Currently comment this line, as when there are wiered cases in which a jobs are in idle for long, it will double the submission!
       os.chdir(path_null) #Come back where you were
     continue
    numFileList = len(fileList)
    #sumNumEvt matches numEvt of the dataset
    rootFilesListFile = file(processName+".txt","w")
    for subdir, dir, files in os.walk('%s' % (outputPathProcessName)):
     for fl in files:
      pathFile = outputPathProcessName+"/"+fl
      if int(os.stat(pathFile).st_size)>1000: print >> rootFilesListFile, "%s/%s" % (outputPathProcessName,fl) #This is for the files to be created and closed correctly
    rootFilesListFile.close()
    rootFilesListFile = file(processName+".txt","r")
    os.system("hadd -ff %s/%s.root @%s.txt" % (outputPathMergedFiles,processName,processName))
    mergedFileName = outputPathMergedFiles+"/"+processName+".root"
    mergedFileSize = int(os.stat(mergedFileName).st_size)
    if not int(os.stat(mergedFileName).st_size)>1000: continue #This is for the files to be merged correctly
    print "Size %s merged from %s files" % (mergedFileSize,numReadyRootFiles)
    try:
     subprocess.check_call(["root -l -q %s/EventCounter.cc+'(\"%s\",\"%s\")'" % (path_utils,outputPathMergedFiles+"/"+processName,"sumNumEvt")], shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    except:
     os.system("eos rm %s.root" % (outputPathMergedFiles+"/"+processName))
     if keep_checking_count==iterations:
      incomplete_datasets = incomplete_datasets+1
      print >> incompleteDataset, "%s %s" % (year,processName)
      print >> incompleteDataset, "Failed to read events"
    else:
     readevt = os.popen("root -l -q %s/EventCounter.cc+'(\"%s\",\"%s\")'" % (path_utils,outputPathMergedFiles+"/"+processName,"sumNumEvt")).read()
     ini,match,readevt = readevt.partition('Read evt are: ')
     readevt = readevt.strip()
     #sumgenWeight matches the known case
     genevt = -1
     if "mc" in dataType:
      genevt = os.popen("root -l -q %s/EventCounter.cc+'(\"%s\",\"%s\")'" % (path_utils,outputPathMergedFiles+"/"+processName,"sumgenWeight")).read()
      ini,match,genevt = genevt.partition('Read evt are: ')
      genevt = genevt.strip()
     rootFilesListFile.close()
     os.system('rm %s' % (rootFilesListFile))
     #3. get keephadd
     keephadd = False
     if "data" in dataType and int(readevt)==datasets_info[d][5]: keephadd = False
     #if "data" in dataType: keephadd = True
     print "before mc %s %s %s %s" % (readevt,datasets_info[d][5],genevt,datasets_info[d][6])
     if "mc" in dataType and float(readevt)/float(datasets_info[d][5])>=evtThMerge and float(genevt)/float(datasets_info[d][6])>=evtThMerge: keephadd = True
     print "%s %s %s" % (year,processName,keephadd)
     print "Files %s %s %s" % (float(numReadyRootFiles)/float(numFileList),numReadyRootFiles,numFileList)
     print "sumNumEvt %s %s %s" % (float(readevt)/float(datasets_info[d][5]),readevt,datasets_info[d][5])
     if "mc" in dataType: print "sumgenWeight %s %s %s" % (float(genevt)/float(datasets_info[d][6]),genevt,datasets_info[d][6])
     if keephadd:
      finished_datasetnames.append(year+"_"+processName)
      merged_datasetnames.append(year+"_"+processName)
      print >> completeDataset, "%s %s" % (year,processName)
      print >> completeDataset, "Files %s %s %s" % (float(numReadyRootFiles)/float(numFileList),numReadyRootFiles,numFileList)
      print >> completeDataset, "sumNumEvt %s %s %s" % (float(readevt)/float(datasets_info[d][5]),readevt,datasets_info[d][5])
      if "mc" in dataType: print >> completeDataset, "sumgenWeight %s %s %s" % (float(genevt)/float(datasets_info[d][6]),genevt,datasets_info[d][6])
      print >> completeDataset, ""
     elif keep_checking_count<iterations:
      os.system("eos rm %s/%s.root" % (outputPathMergedFiles,processName))
      if os.path.isfile(outputPathMergedFiles+"/"+processName+".root"): os.system("mail -s \"%s %s not deleted ;-(\" brandon.j.soubasis@vanderbilt.edu < /dev/null" % (year,processName))
     elif keep_checking_count==iterations:
      incomplete_datasets = incomplete_datasets+1
      os.system("eos rm %s/%s.root" % (outputPathMergedFiles,processName))
      if os.path.isfile(outputPathMergedFiles+"/"+processName+".root"): os.system("mail -s \"%s %s not deleted ;-(\" brandon.j.soubasis@vanderbilt.edu < /dev/null" % (year,processName))
      print >> incompleteDataset, "%s %s" % (year,processName)
      print >> incompleteDataset, "Files %s %s %s" % (float(numReadyRootFiles)/float(numFileList),numReadyRootFiles,numFileList)
      print >> incompleteDataset, "sumNumEvt %s %s %s" % (float(readevt)/float(datasets_info[d][5]),readevt,datasets_info[d][5])
      if "mc" in dataType: print >> incompleteDataset, "sumgenWeight %s %s %s" % (float(genevt)/float(datasets_info[d][6]),genevt,datasets_info[d][6])
      print >> incompleteDataset, "Missing files are:"
      os.chdir(path_at+'/'+year+'/'+processName) #Need to be in this folder to properly resubmit on condor
      #fileList = getDatasetFileList(year,processName)
      for f in fileList:
       head,tail = os.path.split(f)
       fileName = tail.replace('.root','')
       if os.path.isfile(outputPathProcessName+"/"+fileName+"_Skim.root"):
        os.system('rm %s.sh' % (fileName)) #Eliminate the .sh file corresponding to the root files that have already been produced, so that you can re-submit 1 task for the missing files
       else:
        if getoutput('condor_q --nobatch | grep %s' % (fileName)):
         print >> incompleteDataset, "%s (Running on condorHT)" % (fileName)
         os.system('mv %s.sh ..' % (fileName)) #Temporarily move in a different folder as you do not want to be part of the resubmitting of the missing files
        else:
         os.system('cp ./error/%s* %s/failedFiles' % (fileName,path_at))
         os.system('cp ./log/%s* %s/failedFiles' % (fileName,path_at))
         os.system('cp ./output/%s* %s/failedFiles' % (fileName,path_at))
         #prepareSubFile(fileName,year,processName) #This is needed in case you need to resubmit a job on a single file of a dataset
         #os.system("condor_submit %s.cfg" % (fileName))
         print >> incompleteDataset, "%s (Resubmitted on condorHT)" % (fileName)
      print >> incompleteDataset, ""
      os.system("condor_submit %s.cfg" % (processName)) #Resubmit on condorHT the missing files, which are not already running on condorHT
      os.system('mv ../*.sh .') #Copy back the .sh files temporarily moved from the processName folder
  #End Loop over all dataset of interest
  hostname_ = getoutput('hostname')
  if not mergeOnly and keep_checking_count==1: os.system("mail -s \"%s submission finished on %s\" brandon.j.soubasis@vanderbilt.edu < /dev/null" % (task,hostname_))
  if num_datasets_of_interest==len(finished_datasetnames)+already_merged: break
  #isCondorJobs0 = subprocess.Popen(['condor_q | grep "0 jobs; 0 completed, 0 removed, 0 idle, 0 running, 0 held, 0 suspended"'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  #(outIsCondorJobs0, errIsCondorJobs0) = isCondorJobs0.communicate()
  #if "0 jobs; 0 completed, 0 removed, 0 idle, 0 running, 0 held, 0 suspended" in outIsCondorJobs0:
  # mergeOnly = True
  # keep_checking_count = iterations
  # timeSleep = '1s'
  os.system("sleep %s" % (timeSleep)) #Num in sec
 #If all data datasets are read, merged them into data.root
 #numDataDatasets = 0
 #numProcessedDataDatasets = 0
 #for d in range(0,len(datasets_info)):
 # #Choose analysis
 # if not analysis in datasets_info[d][7]: continue
 # #Choose year
 # year = str(datasets_info[d][0])
 # if not year in years: continue
 # #Choose datasetFlag
 # if not (datasetFlag==datasets_info[d][1] or datasetFlag=="All"): continue
 # #Get some more info
 # processName = datasets_info[d][2]
 # outputPathMergedFiles = "/eos"+lnfPath+analysis+"/"+task+"/"+year+"/"+"mergedFiles"
 # datasetName = datasets_info[d][3]
 # if "NANOAOD" in datasetName and not "NANOAODSIM" in datasetName: #Means: dataType="data" #We keep also "NANOAOD" in datasetName as we want to be sure of the dataset to be used
 #  mergeData = True
 # if "NANOAODSIM" in datasetName: #Means: dataType="mc".
 #                                 #We know that MC samples come after data samples in datasets_info.py, so can exploit this feauture to create data.root for different years
 #                                 #Note that if you run with -df dataLable (e.g. "MET") you will not pass this if and will not create the data.root file
 #  if numDataDatasets==numProcessedDataDatasets:
 #   if mergeData:
 #    os.system("hadd -ff %s/data.root %s/%s*" % (outputPathMergedFiles,outputPathMergedFiles,datasets_info[d-1][1]))
 #    mergeData = False
 #  else:
 #   os.system("data.root is missing in year %s" % (year))
 #  continue
 # #Count numDataDatasets and numProcessedDataDatasets
 # numDataDatasets = numDataDatasets+1
 # if os.path.isfile(outputPathMergedFiles+"/"+processName+".root"): numProcessedDataDatasets = numProcessedDataDatasets+1
 print ""
 print "Now 1. Check rootFiles are readable 2. Create data.root files 3. Print weights for MC samples"

 #Now 1. Check rootFiles are readable 2. Create data.root files 3. Print weights for MC samples
 #1. Check rootFiles are readable
 good_datasets = 0
 goodDatasetName = '%sselection/%s_%s_goodDatasets.txt' % (path_fw,task,years)
 if os.path.isfile(goodDatasetName): os.system("rm %s" % (goodDatasetName))
 goodDataset = file(goodDatasetName,"a+")
 bad_datasets = 0
 badDatasetName = '%sselection/%s_%s_badDatasets.txt' % (path_fw,task,years)
 if os.path.isfile(badDatasetName): os.system("rm %s" % (badDatasetName))
 badDataset = file(badDatasetName,"a+")
 year_change = ""
 #2. Create data.root
 all_datasets_for_dataproot = 0
 good_datasets_for_dataproot = 0
 #3. Print weights for MC samples
 infoDatasetName = '%sselection/%s_%s_infoDatasets.txt' % (path_fw,task,years)
 if os.path.isfile(infoDatasetName): os.system("rm %s" % (infoDatasetName))
 infoDataset = file(infoDatasetName,"a+")
 samples ="const char *samples[]  = {"
 lumiWeights = "const double lumiWeights[100] = {"
 sumgenWeights = "const double sumgenWeights[100] = {"
 for d in range(0,len(datasets_info)):
  #Choose analysis
  if not analysis in datasets_info[d][7]: continue
  #Choose year
  year = str(datasets_info[d][0])
  if not year in years: continue
  outputPathMergedFiles = "/eos"+lnfPath+analysis+"/"+task+"/"+year+"/"+"mergedFiles"
  #2. Create data.root files
  if good_datasets==0 and bad_datasets==0: #This means if it is the first entry you parse
   year_change = str(datasets_info[d][0])
  else:
   if datasets_info[d][1] is not datasetFlagData and not os.path.isfile("%s/data.root" % (outputPathMergedFiles)) and datasetFlagData!='None':
    if all_datasets_for_dataproot==good_datasets_for_dataproot: os.system("hadd -ff %s/data.root %s/%s*" % (outputPathMergedFiles,outputPathMergedFiles,datasetFlagData))
   if year_change!=str(datasets_info[d][0]): #It does not consider last year here (need to add the part you want to run for last year outside the loop for d in range(0,len(datasets_info)):)
    #print year_change
    print >> infoDataset, "%s" % (year_change)
    year_change = str(datasets_info[d][0])
    all_datasets_for_dataproot = 0
    good_datasets_for_dataproot = 0
    #3. Print weights for MC samples
    samples = samples+'"data"};'
    #print samples
    print >> infoDataset, "%s" % (samples)
    lumiWeights = lumiWeights[:-1]
    lumiWeights = lumiWeights+',1};'
    #print lumiWeights
    print >> infoDataset, "%s" % (lumiWeights)
    sumgenWeights = sumgenWeights[:-1]
    sumgenWeights = sumgenWeights+',1};'
    #print sumgenWeights
    print >> infoDataset, "%s" % (sumgenWeights)
    #print ""
    print >> infoDataset, " "
    samples ="const char *samples[]  = {"
    lumiWeights = "const double lumiWeights[100] = {"
    sumgenWeights = "const double sumgenWeights[100] = {"
  #Get data type
  processName = datasets_info[d][2]
  datasetName = datasets_info[d][3]
  if "NANOAODSIM" in datasetName: dataType="mc"
  elif "NANOAOD" in datasetName:
   runperiod = processName.replace(datasets_info[d][1],'')
   dataType="data"+runperiod
  else: raise ValueError('Which dataType are you using?')
  #Choose datasetFlag
  if "data" in dataType and not (datasetFlagData==datasets_info[d][1]): continue
  if "mc"   in dataType and not (datasetFlagMC==datasets_info[d][1] or datasetFlagMC=="All"): continue
  if "data" in dataType: all_datasets_for_dataproot = all_datasets_for_dataproot+1
  #Dataset is finished
  if not year+"_"+processName in merged_datasetnames: continue
  #1. Check rootFiles are readable
  try:
   #Note that in python you can not "catch" a seg fault. It's not a mere Exception, it's a fatal error that effectively crashes the interpreter itself.
   #At best, you could perhaps use the `multiprocessing` or `subprocess` (as done below) modules to segregate the part of your program that uses ctypes and then try and recover
   #when you detect that the subprocess has crashed.
   #Instead, if possible, fix the C program and/or ensure that there's not an error in your ctypes interfacing code.
   subprocess.check_call(["root -l -q %s/EventCounter.cc+'(\"%s\",\"%s\")'" % (path_utils,outputPathMergedFiles+"/"+processName,"sumNumEvt")], shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
  except:
   bad_datasets = bad_datasets+1
   print >> badDataset, "%s %s" % (year,processName)
   os.system("eos rm %s/%s.root" % (outputPathMergedFiles,processName))
  else:
   good_datasets = good_datasets+1
   print >> goodDataset, "%s %s" % (year,processName)
   #2. Create data.root files
   if "data" in dataType: good_datasets_for_dataproot = good_datasets_for_dataproot+1
   else:
    #Copy Missing files in years
    #if year==year_from_which_copy_missing_files and next((s for s in missing_files if processName in s), None): #next((s for s in missing_files if processName in s), None) means check if processName is in the list missing_files
    # for mf in missing_files:
    #  if processName in mf:
    #   mfyear = mf.split('_')
    #   themfyear = mfyear[0]
    #   mfoutputPathMergedFiles = "/eos"+lnfPath+analysis+"/"+task+"/"+themfyear+"/"+"mergedFiles"
    #   if not os.path.isfile(mfoutputPathMergedFiles+"/"+processName+".root"): os.system("eos cp %s/%s.root %s/%s.root" % (outputPathMergedFiles,processName,mfoutputPathMergedFiles,processName))
    #3. Print weights for MC samples
    xSec = datasets_info[d][4]
    samples = samples+'"'+str(processName)+'",'
    #Get evt sumgenWeight matches the known case
    genevt = os.popen("root -l -q %s/EventCounter.cc+'(\"%s\",\"%s\")'" % (path_utils,outputPathMergedFiles+"/"+processName,"sumgenWeight")).read()
    ini,match,genevt = genevt.partition('Read evt are: ')
    genevt = genevt.strip()
    sumgenWeights = sumgenWeights+str(genevt)+','
    #Get luminosity
    luminosity = 0
    if year=="2018": luminosity = 59.74*1000 #/pb
    elif year=="2017": luminosity = 41.53*1000 #/pb
    elif year=="2016": luminosity = 35.92*1000 #/pb
    else: raise ValueError('Which year are you considering?')
    #Get lumiWeight
    print "lumiWeight %s %s %s %s %s" % (year,processName,xSec,luminosity,genevt)
    lumiWeight = (float(xSec)*float(luminosity))/float(genevt)
    lumiWeights = lumiWeights+str(lumiWeight)+','
 #This is for the last year, see "(need to add the part you want to run for last year outside the loop for d in range(0,len(datasets_info)):)"
 #print year_change
 print >> infoDataset, "%s" % (year_change)
 samples = samples+'"data"};'
 #print samples
 print >> infoDataset, "%s" % (samples)
 lumiWeights = lumiWeights[:-1]
 lumiWeights = lumiWeights+',1};'
 #print lumiWeights
 print >> infoDataset, "%s" % (lumiWeights)
 sumgenWeights = sumgenWeights[:-1]
 sumgenWeights = sumgenWeights+',1};'
 #print sumgenWeights
 print >> infoDataset, "%s" % (sumgenWeights)
 #print ""
 print >> infoDataset, " "
 print >> infoDataset, "Remember to copy the missing_files information in the corresponding years"


 #mv all .txt file the dedicated folder
 if not os.path.exists('%sselection/%s/%s/txtFiles' % (path_fw,analysis,task)): os.makedirs('%sselection/%s/%s/txtFiles' % (path_fw,analysis,task))

 #Keep track of the data.root files created
 dataproot_outcome = ""
 if datasetFlagData!='None':
  theyears = years.split('_')
  for y in theyears:
   dataproot_file = "/eos"+lnfPath+analysis+"/"+task+"/"+y+"/"+"mergedFiles/data"
   if os.path.isfile(dataproot_file+".root"):
    try:
     subprocess.check_call(["root -l -q %s/EventCounter.cc+'(\"%s\",\"%s\")'" % (path_utils,dataproot_file,"sumNumEvt")], shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    except:
     os.system("eos rm %s.root" % (dataproot_file))
     dataproot_outcome = dataproot_outcome+" "+str(y)+" Wrong "
    else:
     readevt = os.popen("root -l -q %s/EventCounter.cc+'(\"%s\",\"%s\")'" % (path_utils,dataproot_file,"sumNumEvt")).read()
     ini,match,readevt = readevt.partition('Read evt are: ')
     readevt = readevt.strip()
     totEvtData = 0
     for d in range(0,len(datasets_info)):
      if not analysis in datasets_info[d][7]: continue
      if str(y)!=str(datasets_info[d][0]): continue
      if datasetFlagData!=datasets_info[d][1]: continue
      totEvtData = totEvtData+datasets_info[d][5]
     if int(readevt)==totEvtData: dataproot_outcome = dataproot_outcome+" "+str(y)+" Yes "
     else:
      dataproot_outcome = dataproot_outcome+" "+str(y)+" Wrong evt "
      os.system("eos rm %s.root" % (dataproot_file))
   else: dataproot_outcome = dataproot_outcome+" "+str(y)+" Not produced "
   os.popen('mv %s/selection/*%s*.txt %sselection/%s/%s/txtFiles' % (path_fw,y,path_fw,analysis,task))

 os.chdir(path_utils)
 #os.popen("sh clean.sh")

 #mv all .txt file the dedicated folder
 #if not os.path.exists('%sselection/%s/%s/txtFiles' % (path_fw,analysis,task)): os.makedirs('%sselection/%s/%s/txtFiles' % (path_fw,analysis,task))
 #os.popen('mv %s/selection/*.txt %sselection/%s/%s/txtFiles' % (path_fw,path_fw,analysis,task))

 #At the end, notify me of outcome by mail
 hostname = getoutput('hostname')
 os.system("mail -s \"%s: Initial %s Finished %s (Readable %s Bad %s) Incomplete %s Null %s (%sx%s) data.root %s (%s) \" brandon.j.soubasis@vanderbilt.edu < /dev/null" % (task,num_datasets_of_interest,len(finished_datasetnames)+already_merged,good_datasets,bad_datasets,incomplete_datasets,null_datasets,keep_checking_count,timeSleep,dataproot_outcome,hostname))

def getlumiWeight(dataType,year,xSec,sumgenWeight):
 lumiWeight = 1
 if dataType=="mc":
  if year=='2018': luminosity = 59.74*1000 #/pb
  elif year=='2017': luminosity = 41.53*1000 #/pb
  elif year=='2016': luminosity = 35.92*1000 #/pb
  lumiWeight = (xSec*luminosity)/sumgenWeight
 return lumiWeight

def getDatasetFileList(year,processName):
 command = 'cat %srootFilesList/%s/%s.txt' % (path_utils,year,processName)
 fileList = getoutput(command)
 fileList = fileList.split(os.linesep)
 fileList = ['root://cms-xrd-global.cern.ch/'+f for f in fileList]
 return fileList

def prepareSubDataset(year,processName):
 subFile = file(processName+'.cfg',"w")
 print >> subFile, "universe = vanilla"
 print >> subFile, "executable = $(filename)"
 print >> subFile, "output = output/$Fn(filename).out" #Fn removes the extension of the input file (in this case ".sh")
 print >> subFile, "error = error/$Fn(filename).err"
 print >> subFile, "log = log/$Fn(filename).log"
 #scheduler
 #print >> subFile, "_CONDOR_SCHEDD_HOST=bigbird15.cern.ch"
 #print >> subFile, "_CONDOR_CREDD_HOST=bigbird15.cern.ch"
 #print >> subFile, "getenv = True"
 print >> subFile, "should_transfer_files   = YES"
 print >> subFile, "when_to_transfer_output = ON_EXIT"
 print >> subFile, "transfer_output_remaps = \"$Fn(filename)_Skim.root=/eos%s%s/%s/%s/%s/$Fn(filename)_Skim.root\"" % (lnfPath,analysis,task,year,processName)
 thequeueHours = queueHours
 if "LQ_InclusiveDecay" in processName: thequeueHours = 2*queueHours #TRY this to fix missing signal samples. Otherwise TRY this and condor_submit 2 times as you are trying for the data
 print >> subFile, "+AccountingGroup = \"group_u_CMS.CAF.COMM\""
 print >> subFile, "+MaxRuntime = 60*60*%s" % (thequeueHours) #Time in sec
 #print >> subFile, "+JobFlavour = \"longlunch\""
 #print >> subFile, "request_memory = 2000" #In MB
 print >> subFile, "request_cpus = 1" #n should be equivalent to n*2000 in request_memory
 print >> subFile, "requirements = (OpSysAndVer =?= \"CentOS7\")"
 #print >> subFile, "queue"
 print >> subFile, "queue filename matching files *.sh"

def prepareSubFile(fileName,year,processName):
 subFile = file(fileName+'.cfg',"w")
 print >> subFile, "universe = vanilla"
 print >> subFile, "executable = %s.sh"  % (fileName)
 print >> subFile, "output = output/%s.out" % (fileName)
 print >> subFile, "error = error/%s.err" % (fileName)
 print >> subFile, "log = log/%s.log" % (fileName)
 #print >> subFile, "getenv = True"
 print >> subFile, "should_transfer_files   = YES"
 print >> subFile, "when_to_transfer_output = ON_EXIT"
 print >> subFile, "transfer_output_remaps = \"%s_Skim.root=/eos%s%s/%s/%s/%s/%s_Skim.root\"" % (fileName,lnfPath,analysis,task,year,processName,fileName)
 print >> subFile, "+AccountingGroup = \"group_u_CMS.CAF.COMM\""
 thequeueHours = queueHours
 if "LQ_InclusiveDecay" in processName: thequeueHours = 2*queueHours #TRY this to fix missing signal samples. Otherwise TRY this and condor_submit 2 times as you are trying for the data
 print >> subFile, "+MaxRuntime = 60*60*%s" % (thequeueHours) #Time in sec
 #print >> subFile, "+JobFlavour = \"longlunch\""
 #print >> subFile, "request_memory = 2000" #In MB
 print >> subFile, "request_cpus = 1" #n should be equivalent to n*2000 in request_memory
 print >> subFile, "requirements = (OpSysAndVer =?= \"CentOS7\")"
 print >> subFile, "queue"

def prepareSHFile(f,fileName,year,dataType,processName,lumiWeight):
 subFile = file(fileName+'.sh',"w")
 print >> subFile, "#!/bin/bash"
 #print >> subFile, "set -x ; env ; echo \"CMDLINE -- $@\"" #Command suggested by Andrew Melo. Not sure what it does
 path = os.environ['CMSSW_BASE'] + "/src"
 print >> subFile, "pushd %s" % (path)
 print >> subFile, "eval `scramv1 runtime -sh`"
 print >> subFile, "popd"
 path = path+'/vbfhn-picoframework/selection'
 print >> subFile, "export X509_USER_PROXY=%s/x509up_u106282" % (path)
 print >> subFile, "voms-proxy-info -all"
 print >> subFile, "voms-proxy-info -all -file %s/x509up_u106282" % (path)
 if btagEff:
  #print >> subFile, "python %s/%s_Running.py -p %s -c %s -y %s -dt %s -pn %s -lw %s -bt %s -if %s" % (path,analysis,process,channel,year,dataType,processName,lumiWeight,btagEff,f)
  print >> subFile, "python %s/search_runner.py -p %s -y %s -dt %s -if %s" % (path,process,year,dataType,f)
 else:
  #print >> subFile, "python %s/%s_Running.py -p %s -c %s -y %s -dt %s -pn %s -lw %s -if %s" % (path,analysis,process,channel,year,dataType,processName,lumiWeight,f)
  print >> subFile, "python %s/search_runner.py -p %s -y %s -dt %s -if %s" % (path,process,year,dataType,f)

if __name__ == '__main__':
 main()
