#!/usr/bin/env python
#Notes
#1. the part "/tmp/x509up_u30997" works only on fromeo laptop. If you use this script, make sure it is updated to work on your machine.
#2. It assumes that you set 
#   a. in outputFilePath (suggest an eos area) 
#      genproductions package (see https://twiki.cern.ch/twiki/bin/view/CMS/QuickGuideMadGraph5aMCatNLO#Quick_tutorial_on_how_to_produce)
#      in genproductions/bin/MadGraph5_aMCatNLO/cards/ the ufoModelCase, process and the baseDatacards inside it
#      the baseDatacards must contain a template of generation cards with the files named as process_thirdParZZZ_secondParYYY_firstParXXX_Card.dat
#      and must have the model parameters (up to 3 parameters) set to XXX, YYY, ZZZ inside the cards, as this is the placeholder modified by the script to set the wanted values
#   b. in this folder 
#      Sihyuns's framework
#3. After you create the gridpacks, check they are created correctly in outputFilePath+'genproductions/bin/MadGraph5_aMCatNLO/cards/'
#   then, move manually in outputFilePath+'/gridpacks'+'/'+ufoModelCase+'/'+process (it takes a second to do it, and it does not seem trivial to mv them automatically)
#User input
from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument('-st','--simulationType',dest='simulationType',action='store',choices=['FastSimulation','FullSimulation'],type=str,default='FullSimulation')
parser.add_argument('-s','--step',dest='step',action='store',choices=['gridpack', 'wmLHEGEN__CMSSW_10_6_22', 'GEN__CMSSW_10_6_22', 'SIM__CMSSW_10_6_17_patch1', 'DIGIPremix__CMSSW_10_6_17_patch1', 'HLT__CMSSW_10_2_16_UL', 'RECO__CMSSW_10_6_17_patch1', 'MiniAOD__CMSSW_10_6_17_patch1', 'NanoAODv2__CMSSW_10_6_19_patch2'],type=str,default='gridpack') #Note the steps are sequential from gridpack to NanoAOD, except you have to choose between wmLHEGEN or GEN
parser.add_argument('-gf','--genFragment',dest='genFragment',type=str,default='Hadronizer_TuneCP2_13TeV_generic_LHE_pythia8_cff.py')
parser.add_argument('-ne','--nEvents',dest='nEvents',action='store',type=int,default='10') #not relevant for gridpack
parser.add_argument('-nj','--nJobs',dest='nJobs',action='store',type=int,default='1') #not relevant for gridpack
parser.add_argument('-um','--ufoModelCase',dest='ufoModelCase',action='store',type=str,default='SM_HeavyN_NLO_UFO__mn3') #Note the __ to separate Model and Particle
parser.add_argument('-ac','--archCMSSW',dest='archCMSSW',action='store',type=str,default='slc7_amd64_gcc700_CMSSW_10_6_19_tarball.tar.xz') 
parser.add_argument('-ofp','--outputFilePath',dest='outputFilePath',action='store',type=str,default='/eos/cms/store/group/phys_b2g/azp/hn/simulation/') #gridpackFile = gridpackPath(:outputFilePath+'gridpacks/')+parameters+'_'+archCMSSW 
parser.add_argument('-hd','--homeDir',dest='homeDir',action='store',type=str,default='/afs/cern.ch/user/f/fromeo/') 
parser.add_argument('-qh','--queueHours',dest='queueHours',action='store',type=int,default=24)
parser.add_argument('-i','--iterations',dest='iterations',action='store',type=int,default='1')
parser.add_argument('-ts','--timeSleep',dest='timeSleep',action='store',type=str,default='1s')
parser.add_argument('-r','--run',dest='run',action='store',choices=[True,False],type=bool,default=False) #run over HTcondor
args = parser.parse_args()
simulationType = args.simulationType
#The order (campaigns,step,processes,parameters) follows that of the framework EXO-MCsampleProductions
campaigns = ['RunIISummer20UL18']#RunIISummer20UL16  RunIISummer20UL16APV  RunIISummer20UL17  RunIISummer20UL18 #Not relevant for producing gridpacks 
step = args.step
processes = ['WWFusion']
#processes = ['WGammaFusion']
thirdParName = "none" #It must be 'none' if such case does not exist in your model
thirdPars = ["none"]
secondParName = "coupling" #It must be 'none' if such case does not exist in your model
secondPars = [0.1,1]
firstParName = "mass" #It must something
firstPars = [1000,10000]
#firstPars = [500,1000]
genFragment = args.genFragment
nEvents = args.nEvents
nJobs = args.nJobs
ufoModelCase = args.ufoModelCase
archCMSSW = args.archCMSSW
outputFilePath = args.outputFilePath
homeDir = args.homeDir
queueHours = args.queueHours
iterations = args.iterations
timeSleep = args.timeSleep
run = args.run
#imports
import os, sys, subprocess
from commands import getoutput
import random
#needed to submit the task
passwd = os.popen('cat /afs/cern.ch/user/f/fromeo/private/vomsproxy').read().strip()
#Run me with python -u (if you go in background)
#step=
#nohup python submitProduction2HTCondor.py -ne 100000 -nj 100 -s "$step" -r True >& "$step".txt & 

#
#main
#
def main():
 stepName = step.split('__',1)[0] #e.g. from wmLHEGEN__CMSSW_10_6_22 to wmLHEGEN
 if(stepName=='gridpack'): 
  for process in processes:
   productionGridpack(process)
 else:
  for campaign in campaigns:
   #
   if(stepName=='wmLHEGEN'): 
    previousStepName = 'gridpack' #not used in this step, so can be any name
    previousStepRootFileName = 'step1_gridpack' #not used in this step, so can be any name
   elif(stepName=='SIM'): 
    previousStepName = 'wmLHEGEN'
    previousStepRootFileName = 'step1_GEN' #Need to see what Sihyun choose for it by running one time this step with a dummy csv file
   elif(stepName=='DIGIPremix'): 
    previousStepName = 'SIM'
    previousStepRootFileName = 'step1_SIM' 
   elif(stepName=='HLT'): 
    previousStepName = 'DIGIPremix'
    previousStepRootFileName = 'step1_RAW' 
   elif(stepName=='RECO'): 
    previousStepName = 'HLT'
    previousStepRootFileName = 'step1_DIGI2RAW' 
   elif(stepName=='MiniAOD'): 
    previousStepName = 'RECO'
    previousStepRootFileName = 'step1_RECO' 
   elif(stepName=='NanoAODv2'): 
    previousStepName = 'MiniAOD'
    previousStepRootFileName = 'step1_PAT' 
   else:
    sys.exit('Which step are you running?')  
   #
   simulationDir = './EXO-MCsampleProductions/'+simulationType+'/'+campaign+'/'+step+'/src/'
   os.chdir(simulationDir)
   for process in processes:
    deleteNonBaseFolders(stepName,process) #it deletes folders created in a previous use of this script that are NOT the default ones of the EXO-MCsampleProductions framework, to clear working directory
    production(campaign,process,stepName,previousStepName,previousStepRootFileName)
   os.chdir('../../../../..') #go back 5 folders, as before os.chdir(simulationDir)

#
#supporting functions
#
def productionGridpack(process):
 #create dirs
 path_at = (os.popen("pwd").read()).strip() #.strip() removes empty characters
 if not os.path.exists('gridpacks'): createDir('gridpacks') #Note this is created in the current folder where the submitProduction2HTCondor.py is 
 else: os.system('rm -r *sh') #delete previous sh scripts, otherwise they will all be run 
 outputDir = outputFilePath+'/gridpacks'
 if not os.path.exists(outputDir): createDir(outputDir)
 outputDir = outputDir+'/'+ufoModelCase
 if not os.path.exists(outputDir): createDir(outputDir)
 outputDir = outputDir+'/'+process
 if not os.path.exists(outputDir): createDir(outputDir)
 #
 workingDir = outputFilePath+'genproductions/bin/MadGraph5_aMCatNLO/cards/'+ufoModelCase+'/'+process
 os.chdir(workingDir) #It assumes you set up outputFilePath as explained in the notes at the beginning of the script  
 for tp in thirdPars:
  tp = str(tp).replace('.','p') #Need to do it as otherwise the system does not understand the '.' in the code
  for sp in secondPars:
   sp = str(sp).replace('.','p')
   for fp in firstPars: 
    fp = str(fp).replace('.','p')
    parameters = defineParameters(tp,sp,fp)
    fileName = '%s_%s' % (process,parameters) #Note you need to keep the process in the fileName, even if it seems redundant as it appears also in the folder name where the gridpack is stored, because it is first created in genproductions/bin/MadGraph5_aMCatNLO and if you have different processes with same parameters you might messed up!
    if os.path.exists('%s/%s' % (workingDir,fileName)): os.system('rm -r %s' % (fileName)) #Always delete folders/files before creating them to clean it up 
    os.system('cp -r baseDatacards %s' % (fileName)) 
    os.chdir('%s' % (fileName))
    #
    #Always delete folders/files before creating them to clean it up
    madDir = outputFilePath+'genproductions/bin/MadGraph5_aMCatNLO/' #where the gridpack output (directory,log file,tar file) will be first created (because I do not know how to create the output in a specific folder)
    if os.path.exists('%s/%s' % (madDir,fileName)): os.system('rm -r %s/%s' % (madDir,fileName)) #directory 
    if os.path.exists('%s/%s.log' % (madDir,fileName)): os.system('rm -r %s/%s.log' % (madDir,fileName)) #log
    if os.path.exists('%s/%s_%s' % (madDir,fileName,archCMSSW)): os.system('rm -r %s/%s_%s' % (madDir,fileName,archCMSSW)) #tar file 
    #outputDir is where the files will be at the end of the script
    if os.path.exists('%s/%s' % (outputDir,fileName)): os.system('rm -r %s/%s' % (outputDir,fileName)) #directory 
    if os.path.exists('%s/%s.log' % (outputDir,fileName)): os.system('rm -r %s/%s.log' % (outputDir,fileName)) #log
    if os.path.exists('%s/%s_%s' % (outputDir,fileName,archCMSSW)): os.system('rm -r %s/%s_%s' % (outputDir,fileName,archCMSSW)) #tar file 
    #
    initializeProxy()
    os.system('mv %s_thirdParZZZ_secondParYYY_firstParXXX_run_card.dat %s_run_card.dat' % (process,fileName)) 
    os.system('mv %s_thirdParZZZ_secondParYYY_firstParXXX_extramodels.dat %s_extramodels.dat' % (process,fileName))    
    os.system('mv %s_thirdParZZZ_secondParYYY_firstParXXX_customizecards.dat %s_customizecards.dat' % (process,fileName)) 
    os.system('sed -i \'s/ZZZ/%s/g\' %s_customizecards.dat' % (tp.replace('p','.'),fileName)) #Need to replace back to '.' as we need numbers here 
    os.system('sed -i \'s/YYY/%s/g\' %s_customizecards.dat ' % (sp.replace('p','.'),fileName))
    os.system('sed -i \'s/XXX/%s/g\' %s_customizecards.dat' % (fp.replace('p','.'),fileName))
    os.system('mv %s_thirdParZZZ_secondParYYY_firstParXXX_proc_card.dat %s_proc_card.dat' % (process,fileName)) 
    os.system('sed -i \'s/thirdPar/%s/g\' %s_proc_card.dat' % (thirdParName,fileName))
    os.system('sed -i \'s/ZZZ/%s/g\' %s_proc_card.dat' % (tp,fileName))
    os.system('sed -i \'s/secondPar/%s/g\' %s_proc_card.dat' % (secondParName,fileName))
    os.system('sed -i \'s/YYY/%s/g\' %s_proc_card.dat' % (sp,fileName))
    os.system('sed -i \'s/firstPar/%s/g\' %s_proc_card.dat' % (firstParName,fileName))
    os.system('sed -i \'s/XXX/%s/g\' %s_proc_card.dat' % (fp,fileName))
    prepareSHFileGridpack(fileName,process)
    os.system('mv %s.sh %s/gridpacks' % (fileName,path_at)) #need to run from afs according to https://batchdocs.web.cern.ch/troubleshooting/eos.html#no-eos-submission-allowed
    # 
    os.chdir('../')
 #create scripts
 os.chdir(path_at+'/gridpacks')
 prepareHTCOutputFolders()
 prepareSubDataset('',1)
 #run on HTcondor
 if(run): os.system("condor_submit submitTask.cfg")
 #come back to initial folder
 os.chdir(path_at)

def deleteNonBaseFolders(stepName,process):
 if os.path.exists('submit_crab_%s.sh' % (process)): os.system('rm submit_crab_%s.sh' % (process))
 if os.path.exists('%s.csv' % (process)): os.system('rm %s.csv' % (process))
 if os.path.exists(process) and os.path.isdir(process): os.system('rm -r %s' % (process))
 if(stepName=='wmLHEGEN'):
  if os.path.exists('./Configuration') and os.path.isdir('./Configuration'): os.system('rm -r Configuration')
  if os.path.exists('run_cmsdriver_%s.sh' % (process)): os.system('rm run_cmsdriver_%s.sh' % (process))

def production(campaign,process,stepName,previousStepName,previousStepRootFileName):
 configFile = 'config_'+stepName+'.py'
 #
 #build cmsDriver command
 #
 gridpackPath = outputFilePath+'gridpacks/'+ufoModelCase+'/'+process+'/'
 prepare_csv(stepName,process,thirdPars,secondPars,firstPars,gridpackPath,archCMSSW,genFragment,nEvents,campaign,previousStepName)
 #adapt config to run over HTcondor and run it
 if(stepName=='wmLHEGEN'): os.system('sed -i \'s/if \\"cvmfs\\" in gridpack:/if \"eos\" in gridpack:/g\' %s' % (configFile)) #Remember we run on HTcondor and have files in eos, not cvmfs
 os.system('python %s %s.csv' % (configFile,process)) #Note that this will create a folder named as the .csv file
 #
 #prepare to run on HTcondor
 #
 outputDir = outputFilePath+campaign
 if not os.path.exists(outputDir): createDir(outputDir)
 outputDir = outputDir+'/'+stepName
 if not os.path.exists(outputDir): createDir(outputDir)
 outputDir = outputDir+'/'+process
 if not os.path.exists(outputDir): createDir(outputDir)
 for tp in thirdPars:
  tp = str(tp).replace('.','p') #Need to do it as otherwise the system does not understand the '.' in the code
  if(tp!="none"):
   outputDir = outputDir+'/'+thirdParName+str(tp)
   if not os.path.exists(outputDir): createDir(outputDir)
  for sp in secondPars:
   sp = str(sp).replace('.','p')
   if(sp!="none"):
    outputDir = outputDir+'/'+secondParName+str(sp)
    if not os.path.exists(outputDir): createDir(outputDir)
   for fp in firstPars:
    fp = str(fp).replace('.','p')
    if(fp!="none"):
     outputDir = outputDir+'/'+firstParName+str(fp)+'/'
     if os.path.exists(outputDir) and os.path.isdir(outputDir): os.system('rm -r %s' % (outputDir)) #Always delete folders/files before creating them to clean it up
     createDir(outputDir)
    else:
     sys.exit('Which parameters are you running?') 
    parameters = defineParameters(tp,sp,fp)    
    sampleName = process+'/'+parameters
    createDir(sampleName)
    os.chdir(sampleName)
    initializeProxy()
    evtPerJob = nEvents/nJobs #it is ok not to cast, as we want int anyway below
    for j in range(0,nJobs): 
     jobInFileName = previousStepName+'_'+str(j) #not needed in wmLHEGEN step
     jobOutFileName = stepName+'_'+str(j)
     createDir(jobOutFileName)
     htcName = jobOutFileName+'.py'
     os.system('cp run_crab.py %s/%s' % (jobOutFileName,htcName))
     if(stepName=='wmLHEGEN'):
      os.system('sed -i \'s/%s.root/%s%s.root/g\' %s/%s' % (stepName,outputDir.replace('/','\/'),jobOutFileName,jobOutFileName,htcName)) #output
      newSeed = str(random.randint(1, 100000)) 
      os.system('sed -i \'s/initialSeed=.*/initialSeed=%s/g\' %s/%s' % (newSeed,jobOutFileName,htcName)) #seed value 
      os.system('sed -i \'s/nEvents = cms\.untracked\.uint32(.*),/nEvents = cms\.untracked\.uint32(%s),/g\' %s/%s' % (evtPerJob,jobOutFileName,htcName)) #nuber of events 
     else:
      os.system('sed -i \'s/%s.root/%s%s.root/g\' %s/%s' % (previousStepRootFileName,(outputDir.replace(stepName,previousStepName)).replace('/','\/'),jobInFileName,jobOutFileName,htcName)) #input 
      os.system('sed -i \'s/%s.root/%s%s.root/g\' %s/%s' % (stepName,outputDir.replace('/','\/'),jobOutFileName,jobOutFileName,htcName)) #output
      os.system('sed -i \'s/input = cms\.untracked\.int32(.*)/input = cms\.untracked\.int32(%s)/g\' %s/%s' % (evtPerJob,jobOutFileName,htcName)) #nuber of events 
     os.system('sed -i \"s/nevts:.*\'),/nevts:%s\'),/g\" %s/%s' % (evtPerJob,jobOutFileName,htcName)) #nuber of events 
     #create scripts
     prepareHTCOutputFolders()
     prepareSHFile(jobOutFileName)
    prepareSubDataset(outputDir,0)
    #
    #run on HTcondor
    #
    if(run): os.system("condor_submit submitTask.cfg")
    #restore things as before the for loop on firstPars
    os.chdir('../..') #go back 2 folders, as before os.chdir(sampleName)
    outputDir = outputDir.replace('/'+firstParName+str(fp)+'/','') #remove the current firstPars or next firstPars will be inside it
   outputDir = outputDir.replace('/'+secondParName+str(sp),'') #remove the current secondPars or next secondPars will be inside it
  outputDir = outputDir.replace('/'+thirdParName+str(tp),'') #remove the current thirdPars or next thirdPars will be inside it

def prepare_csv(stepName,process,thirdPars,secondPars,firstPars,gridpackPath,archCMSSW,genFragment,nEvents,campaign,previousStepName):
 #Prepare the required csv file
 csvFile = file(process+'.csv',"w")
 for tp in thirdPars:  
  tp = str(tp).replace('.','p') #Need to do it as otherwise the system does not understand the '.' in the code
  for sp in secondPars:
   sp = str(sp).replace('.','p')
   for fp in firstPars:
    fp = str(fp).replace('.','p')
    parameters = defineParameters(tp,sp,fp)
    csvFileContent = ''
    if(stepName=='wmLHEGEN'):
     gridpackFile = gridpackPath+process+'_'+parameters+'_'+archCMSSW 
     csvFileContent = parameters+','+genFragment+','+str(nEvents)+','+str(nJobs)+','+gridpackFile #NB nEvents and nJobs must be added to setup the csv file as expected, and not effect on how you split the events/jobs on HTcondor!
    else:
     csvFileContent = parameters+','+parameters+'_'+campaign+'_'+previousStepName #NB these are placeholder values to comply with the EXO-MCsampleProductions framework. They are not meaningful 
    print >> csvFile, csvFileContent 

def defineParameters(tp,sp,fp):
 parameters = ''
 thirdPar = ''
 if(tp!="none"):
  thirdPar = thirdParName+str(tp)
 secondPar = ''
 if(sp!="none"):
  if(tp!="none"): secondPar = '_'+secondParName+str(sp)
  else: secondPar = secondParName+str(sp)
 firstPar = ''
 if(fp!="none"):
  if(sp!="none"): firstPar = '_'+firstParName+str(fp)
  else: firstPar = firstParName+str(fp)
 else:
  sys.exit("which parameters are you running?")
 parameters = '%s%s%s' % (thirdPar,secondPar,firstPar)
 return parameters
#
#HTcondor
#
def initializeProxy():
 #You must initialize the proxy (and apparently more than just the first time when you run on the queue)
 os.system('echo %s | voms-proxy-init --valid 192:00 -voms cms -rfc' % (passwd)) #192 means keep the credentials valid for 192h
 os.system("cp /tmp/x509up_u30997 .")

def prepareHTCOutputFolders():
 if not os.path.exists("error"): os.makedirs("error") #Do it here to avoid conflicts with !(*cfg) in prepareSubDataset
 if not os.path.exists("log"): os.makedirs("log")
 if not os.path.exists("output"): os.makedirs("output")

def prepareSHFileGridpack(jobOutFileName,process):
 subFile = file(jobOutFileName+'.sh',"w")
 print >> subFile, "#!/bin/bash"
 #print >> subFile, "set -x ; env ; echo \"CMDLINE -- $@\"" #Command suggested by Andrew Melo. Not sure what it does
 path_at = (os.popen("pwd").read()).strip() #.strip() removes empty characters 
 print >> subFile, "pushd %sgenproductions/bin/MadGraph5_aMCatNLO/" % (outputFilePath)
 print >> subFile, "export X509_USER_PROXY=%s/x509up_u30997" % (path_at)
 print >> subFile, "voms-proxy-info -all"
 print >> subFile, "voms-proxy-info -all -file %s/x509up_u30997" % (path_at)
 print >> subFile, "./gridpack_generation.sh %s cards/%s/%s/%s" % (jobOutFileName,ufoModelCase,process,jobOutFileName)
 #It seems none of the below options would easily work, so perhaps wait that the job finishes and then copy manually as it takes a second to mv the output from eos folders
 #print >> subFile, "sleep 3600"
 #gridpackPath = outputFilePath+'gridpacks/'+ufoModelCase+'/'+process+'/'
 #print >> subFile, "mv %sgenproductions/bin/MadGraph5_aMCatNLO/%s* %s" % (outputFilePath,jobOutFileName,gridpackPath)
 #Need to do the check,copy,delete steps, as it seems sometimes it does not copy all the files
 #print >> subFile, "ls %s%s*" % (gridpackPath,jobOutFileName)
 #print >> subFile, "varExist=`echo $?`"
 #print >> subFile, "if [ $varExist == 0 ]; then rm -r %s%s*; fi" % (gridpackPath,jobOutFileName)
 #print >> subFile, "cp -r %sgenproductions/bin/MadGraph5_aMCatNLO/%s* %s" % (outputFilePath,jobOutFileName,gridpackPath)
 #print >> subFile, "ls %s%s*" % (gridpackPath,jobOutFileName)
 #print >> subFile, "varExist=`echo $?`"
 #print >> subFile, "if [ $varExist == 0 ]; then rm -r %sgenproductions/bin/MadGraph5_aMCatNLO/%s*; fi" % (outputFilePath,jobOutFileName)

def prepareSHFile(jobOutFileName):
 subFile = file(jobOutFileName+'.sh',"w")
 print >> subFile, "#!/bin/bash"
 #print >> subFile, "set -x ; env ; echo \"CMDLINE -- $@\"" #Command suggested by Andrew Melo. Not sure what it does
 path_at = (os.popen("pwd").read()).strip() #.strip() removes empty characters 
 print >> subFile, "pushd %s" % (path_at+'/'+jobOutFileName+'/')
 print >> subFile, "eval `scramv1 runtime -sh`"
 print >> subFile, "popd"
 print >> subFile, "export X509_USER_PROXY=%s/x509up_u30997" % (path_at)
 print >> subFile, "export HOME=%s" % (homeDir) #Need this line, if you do not want to fail w/ exit code 6 as explained here https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideCrabFaq 
 print >> subFile, "voms-proxy-info -all"
 print >> subFile, "voms-proxy-info -all -file %s/x509up_u30997" % (path_at)
 print >> subFile, "cmsRun %s/%s.py" % (path_at+'/'+jobOutFileName,jobOutFileName)

def prepareSubDataset(outputDir,isGridpack):
 subFile = file('submitTask.cfg',"w")
 print >> subFile, "universe = vanilla"
 print >> subFile, "executable = $(filename)" 
 print >> subFile, "output = output/$Fn(filename).out" #Fn removes the extension of the input file (in this case ".sh")
 print >> subFile, "error = error/$Fn(filename).err"
 print >> subFile, "log = log/$Fn(filename).log"
 #scheduler
 #print >> subFile, "_CONDOR_SCHEDD_HOST=bigbird15.cern.ch"
 #print >> subFile, "_CONDOR_CREDD_HOST=bigbird15.cern.ch"
 #print >> subFile, "getenv = True"
 if(isGridpack):
  print >> subFile, "should_transfer_files   = No"
 else:
  print >> subFile, "should_transfer_files   = YES"
  print >> subFile, "when_to_transfer_output = ON_EXIT"
  print >> subFile, "transfer_output_remaps = \"$Fn(filename).root=%s$Fn(filename).root\"" % (outputDir)
 thequeueHours = queueHours
 #if "LQ_InclusiveDecay" in processName: thequeueHours = 2*queueHours #TRY this to fix missing signal samples. Otherwise TRY this and condor_submit 2 times as you are trying for the data
 print >> subFile, "+AccountingGroup = \"group_u_CMS.CAF.COMM\""
 print >> subFile, "+MaxRuntime = 60*60*%s" % (thequeueHours) #Time in sec  
 #print >> subFile, "+JobFlavour = \"longlunch\"" 
 #print >> subFile, "request_memory = 2000" #In MB
 print >> subFile, "request_cpus = 1" #n should be equivalent to n*2000 in request_memory
 print >> subFile, "requirements = (OpSysAndVer =?= \"CentOS7\")"
 #print >> subFile, "queue" 
 print >> subFile, "queue filename matching files *.sh"

#
#General functions
#
def createDir(dirName):
 if not os.path.exists(dirName): os.makedirs(dirName)
 else: print('folder %s exists' % (dirName)) 

if __name__ == '__main__':
 main()
