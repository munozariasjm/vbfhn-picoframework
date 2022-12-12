/**
This Macro   
1. Plots variables in stack mode with full error (stat.+sys.) 

Need to specify
1. See Declare Constants
2. The TH1F corresponding to the main contributions (sig, bkg, data) in your analysis. See:
   . get_th1fSR_variations (input, //Simulation, //Data)
   . //Print
   . //Plot
3. The contributions from simulation and data-driven. See isNotDataDriven.
4. In get_evt
   . //Increase/descrese based on the weights you use in the analysis
   . //Selection
   . isNotDataDriven
5. entries_errors

Notes
. genWeight is not specified in Declare Constants as it has to be always used
. The macro assumes all the weights are set to 1 for data, so that you can leave the code as it is when filling the histos for data

Add
. plot with asym bin
. save rootplas for limit
. adattarla per runnare i vari anni
*/
/////
//   To run: root -l stackPlots.cc+  
/////
/////
//   Prepare Root and Roofit
/////
#include "TFile.h"
#include "TH1F.h"
#include "THStack.h"
#include "TLegend.h"
#include "TTree.h"
#include "TTreePlayer.h"
#include "TStyle.h"
#include "TGaxis.h"
#include "TCanvas.h"
#include "TGraphErrors.h"
#include "TGraphAsymmErrors.h"
#include "TEfficiency.h"
#include "TBranch.h"
#include "TLatex.h"
#include "TROOT.h"
#include "Math/DistFunc.h"
#include <fstream>
#include <iostream>
#include <iomanip>
#include <iostream>
using namespace std;
/////
//   Declare constants
/////
const string task         = "Main_TauDz/";
const string taskFakaRate = "FakeRate_TauDzMedium";
const int tauTWP = 8;
const int tauLWP = 2;
const string year      = "2018/";
int numSigs            = 1; //Signals have to enter the first in *samples
int numTTbar           = 15;
int numWJets           = 7;
int numOthers          = 33;
const char *samples[]  = {"SingleVectorLQ_InclusiveDecay_M-500","tZq_Zhad_Wlept_4f_ckm_NLO","TTTo2L2Nu","TTToHadronic","TTToSemiLeptonic","TTWJetsToLNu","TTWJetsToQQ","TTZToLLNuNu","TTZToQQ","TTGJets","TTTT","ST_t-channel_top_4f_InclusiveDecays","ST_t-channel_antitop_4f_InclusiveDecays","ST_tW_top_5f_inclusiveDecays","ST_tW_antitop_5f_inclusiveDecays","ST_s-channel_4f_leptonDecays","WJetsToLNu_HT-100To200","WJetsToLNu_HT-200To400","WJetsToLNu_HT-400To600","WJetsToLNu_HT-600To800","WJetsToLNu_HT-800To1200","WJetsToLNu_HT-1200To2500","WJetsToLNu_HT-2500ToInf","DYJetsToLL_M-4to50_HT-100to200","DYJetsToLL_M-4to50_HT-200to400","DYJetsToLL_M-4to50_HT-400to600","DYJetsToLL_M-4to50_HT-600toInf","DYJetsToLL_M-50_HT-100to200","DYJetsToLL_M-50_HT-200to400","DYJetsToLL_M-50_HT-400to600","DYJetsToLL_M-50_HT-600To800","DYJetsToLL_M-50_HT-800To1200","ZJetsToNuNu_HT-100To200","ZJetsToNuNu_HT-200To400","ZJetsToNuNu_HT-600To800","ZJetsToNuNu_HT-800To1200","ZJetsToNuNu_HT-1200To2500","ZJetsToNuNu_HT-2500ToInf","ZZTo2L2Nu","ZZTo2L2Q","ZZTo2Q2Nu","ZZTo4L","WZTo1L3Nu","WZTo2L2Q","WZTo3LNu","WWTo2L2Nu","WWTo4Q","WWToLNuQQ","WWW","WWZ","WZZ","ZZZ","DYJetsToLL_M-50_HT-1200To2500","DYJetsToLL_M-50_HT-2500ToInf","ZJetsToNuNu_HT-400To600","WZTo1L1Nu2Q","data"}; 
const double lumiWeights[100] = {0.0679404119156,0.00449900938297,0.0925632098679,0.174727473548,0.223135234967,0.00454372686,0.0529572481701,0.00240805470664,0.0890820998463,0.119876432042,0.000609540696132,0.0563922904578,0.0651507474423,0.237986743022,0.299637646972,0.0176616575687,3.44051895861,1.25104755881,0.622042475206,0.0376032587569,0.0412210527172,0.00807149839076,0.000464201788939,1.5073061037,1.16640616225,0.106870904523,0.0347799261077,1.10682168026,0.348745047603,0.0445015856323,0.0100822755805,0.0126484484981,1.24150260651,0.303627532925,0.0453857890722,0.048806192684,0.0554737850497,0.00123117947781,0.00402750296473,0.0108043710707,0.00660953325388,0.0108614212528,0.19823497966,0.0209414124952,0.0436243627528,0.0831863176273,0.814337080772,0.145130010703,0.0593134888149,0.0448505024783,0.0151631972634,0.00389750515676,0.00801083765721,0.000289743704745,0.0642536546449,0.0392714384531,1};
double SF_ttbar        = 0.89067; 
double SF_WJets        = 1.06861;
//Path 
const string lnfpath   = "/eos/cms/store/group/phys_exotica/";
const string analysis  = "LQtop/";
const bool nodata      = false;  
const string path      = lnfpath+analysis+task+year+"mergedFiles/";
//Weights and trees
const int wen = 7;
string weights[100] = {"puWeight","btagWeightL","tauWeight","topWeight","ewkWeight","HEMWeight","prefiringWeight"};
//string weights[100] = {"puWeight","btagWeightDeepFlavourL","tauWeight","topWeight","ewkWeight","HEMWeight","prefiringWeight"};
//Add sys
const bool addsys = true;
const int wsen = 3;//11;//9;
const string weights_sys[wsen] = {"main","puWeightUp","puWeightDown"};//,"btagWeightLUp","btagWeightLDown","tauWeightUp","tauWeightDown","topWeightUp","topWeightDown","prefiringWeightUp","prefiringWeightDown"}; //"main" is needed to include the central value in the weight combination. "main" must be the first in the list.
const int ten = 1;//11;
const string trees[ten] = {"Events"};//,"EventsJesUp","EventsJesDo","EventsJerUp","EventsJerDo","EventsWtagJmsUp","EventsWtagJmsDo","EventsWtagJmrUp","EventsWtagJmrDo","EventsTauScaleUp","EventsTauScaleDo"}; //The tree "Events" must be the first in the list
//Variables
const unsigned int ini_var = 8;
const unsigned int fin_var = 9; 
const int    numVar = 10;
const char *variables[]         = {
"PV_npvsGood", "MET_pt", "massT", "deltaPhiMetTop", "numBjetsL", "numBjetsM", "numBjetsT", "tauPt", "STmet", "numTopJets"
};
const char *titleXaxis[]        = {
"PV_npvsGood", "MET_pt", "massT", "deltaPhiMetTop", "numBjetsL", "numBjetsM", "numBjetsT", "tauPt", "STmet", "numTopJets"
};
const int    bin[numVar]        = {
80, 150, 100, 80, 10, 10, 10, 100, 100, 5 
};
const double inRange[numVar]    = {
0, 0, 0, -4, 0, 0, 0, 0, 0, 0 
};
const double endRange[numVar]   = {
80, 1500, 1000, 4, 10, 10, 10, 500, 1500, 5
};
//Plots
const bool save_plots   = false;
const bool show_title   = true;
const bool logYscale    = false;
const bool doasym       = false; 
const double asymbin[6] = {0,3,4,9,15,20};
/////
//   Declare functions 
/////
//Call TFile to be read
TFile* Call_TFile(string rootpla);
//Get the TH1F of all the contributions in the SignalRegion and the systematic errors
void get_th1fSR_variations(TH1F* LQLQ1p5,TH1F* TTbar,TH1F* WJets,TH1F* Others,TH1F* dataDriven,TH1F* data,vector<vector<vector<double>>> &systematics_processes_bins,string variable,int varPos,vector<vector<string>> allWeights,bool isNotDataDriven);
void get_evt(TTree* tree,string variable,int samplePos,int varPos,vector<vector<string>> allWeights,int ws,bool isNotDataDriven,TH1F *hist,TH1F *hist_err,TH1F *hist_err2);
void get_correctionFactor(double pt,double eta, double& correctionFactor, double& correctionFactorErr);
//Print entries and errors and get total errors (stat. and sys.)
void entries_errors(TH1F* LQLQ1p5,TH1F* TTbar,TH1F* WJets,TH1F* Others,TH1F* dataDrivenDD,TH1F* SumBkgs,TH1F* data,int varPos, vector<vector<vector<double>>> systematics_processes_bins,vector<double> &SumBkgs_errStatSysBins);
//Draw the plots  
void draw_plots(TH1F* LQLQ1p5,TH1F* TTbar,TH1F* WJets,TH1F* Others,TH1F* dataDrivenDD,TH1F* SumBkgs,TH1F* data,int varPos,vector<double> &SumBkgs_errStatSysBins);
TGraphAsymmErrors* get_gData(TH1F* data); 
TGraphAsymmErrors* get_ratios(int varPos,TGraphAsymmErrors* gData,TH1F* data,TH1F* SumBkgs,vector<double> SumBkgs_errStatSysBins,TH1F* ratioUnityStatErr,TH1F* ratioUnityStatSysErr);
THStack* get_hstack(TH1F* TTbar,TH1F* WJets,TH1F* dataDrivenDD,TH1F* Others);
double get_maxy(TH1F* data, TH1F* SumBkgs);
void get_marginsForLatex(float &t, float &b, float &r, float &l);
//Get parts of the plot (pad, legends, histo)
TPad* get_pad(string name,string title,double xLow,double yLow,double xUp,double yUp,double topMargin,double bMargin,double rMargin,double lMargin);
TLegend* get_legend();
TH1F* get_th1f(string name,string var,int v);
/////
//   Main function
/////
void stackPlots(){
 //For the systematics related to variations of the weights 
 vector<vector<string>> allWeights;
 for(uint ws=0; ws<wsen; ws++){
  if(!addsys && ws>=1) break;
  vector<string> weights_; weights_.clear();
  for(uint w=0; w<wen; w++){if(weights_sys[ws].find(weights[w])!=std::string::npos){weights_.push_back(weights_sys[ws]);}else{weights_.push_back(weights[w]);}};
  allWeights.push_back(weights_);
 }
 //Loop over all variables
 vector<string> vars(variables, variables + sizeof(variables)/sizeof(variables[0]));
 for(uint vr=ini_var; vr<fin_var; vr++){
  cout<<vars[vr]<<endl;
  //Events in the signal region from simulation
  bool isNotDataDriven = true;  
  TH1F* LQLQ1p5    = get_th1f("LQLQ1p5",vars[vr],vr); 
  TH1F* TTbar      = get_th1f("TTbar",vars[vr],vr); TTbar->SetLineColor(kGreen+3); TTbar->SetFillColor(kGreen+3);
  TH1F* WJets      = get_th1f("WJets",vars[vr],vr); WJets->SetLineColor(kCyan-4); WJets->SetFillColor(kCyan-4);
  TH1F* Others     = get_th1f("Others",vars[vr],vr); Others->SetLineColor(kOrange); Others->SetFillColor(kOrange);
  TH1F* dataDriven = get_th1f("dataDriven",vars[vr],vr); //This is not used in the first call of get_th1fSR_variations
  TH1F* data       = get_th1f("data",vars[vr],vr); data->SetLineWidth(2); data->SetLineColor(1); data->SetMarkerColor(1); data->SetMarkerStyle(20);  
  vector<vector<vector<double>>> systematics_processes_bins;
  get_th1fSR_variations(LQLQ1p5,TTbar,WJets,Others,dataDriven,data,systematics_processes_bins,vars[vr],vr,allWeights,isNotDataDriven);
  //Events in the signal region from data-driven method (jet->tau misIdentification)
  isNotDataDriven = false;
  TH1F* LQLQ1p5DD    = get_th1f("LQLQ1p5DD",vars[vr],vr);
  TH1F* TTbarDD      = get_th1f("TTbarDD",vars[vr],vr);
  TH1F* WJetsDD      = get_th1f("WJetsDD",vars[vr],vr);
  TH1F* OthersDD     = get_th1f("OthersDD",vars[vr],vr);
  TH1F* dataDrivenDD = get_th1f("dataDrivenDD",vars[vr],vr); dataDrivenDD->SetLineColor(kGreen-3); dataDrivenDD->SetFillColor(kGreen-3);
  TH1F* dataDD       = get_th1f("dataDD",vars[vr],vr);
  get_th1fSR_variations(LQLQ1p5DD,TTbarDD,WJetsDD,OthersDD,dataDrivenDD,dataDD,systematics_processes_bins,vars[vr],vr,allWeights,isNotDataDriven);
  //for(int dDD=0; dDD<dataDrivenDD->GetNbinsX(); dDD++) if(dataDrivenDD->GetBinContent(dDD+1)<0) dataDrivenDD->SetBinContent(dDD+1,0);
  //Sum bkg
  TH1F* SumBkgs = get_th1f("SumBkgs",vars[vr],vr);
  SumBkgs->Sumw2();
  SumBkgs->Add(SumBkgs,TTbar);
  SumBkgs->Add(SumBkgs,WJets);
  SumBkgs->Add(SumBkgs,dataDrivenDD);
  SumBkgs->Add(SumBkgs,Others);
  //Get errors and prepare rootfiles for combine 
  vector<double> SumBkgs_errStatSysBins;
  entries_errors(LQLQ1p5,TTbar,WJets,Others,dataDrivenDD,SumBkgs,data,vr,systematics_processes_bins,SumBkgs_errStatSysBins);
  //Plot 
  draw_plots(LQLQ1p5,TTbar,WJets,Others,dataDrivenDD,SumBkgs,data,vr,SumBkgs_errStatSysBins); 
 }
}
/////
//   Call TFile to be read
/////
TFile* Call_TFile(string rootpla){
 string file_name = path+rootpla+".root";
 TFile* f = new TFile(file_name.c_str(),"update");
 return f;
}
/////
//   Get the TH1F of all the contributions in the SignalRegion and the systematic errors
/////
void get_th1fSR_variations(TH1F* LQLQ1p5,TH1F* TTbar,TH1F* WJets,TH1F* Others,TH1F* dataDriven,TH1F* data,vector<vector<vector<double>>> &systematics_processes_bins,string variable,int varPos,vector<vector<string>> allWeights,bool isNotDataDriven){
 int systematic = 0;
 //For the systematics related to variations that require re-running the full analysis and thus have different trees
 for(uint t=0; t<ten; t++){
  if(!addsys && trees[t]!="Events") break; //It assumes that the tree "Events" is the first to be parsed
  for(uint ws=0; ws<wsen; ws++){//For the systematics related to variations of the weights
   if(!addsys && trees[t]=="Events" && weights_sys[ws]!="main") break; //If tree is not "Events", we do not consider systematics related to variations in the weights. It assumes that "main" is the first
   if(trees[t]!="Events" && weights_sys[ws]!="main") break; //Systematics related to variations of the weights applies only to the central Tree called "Events". It assumes that "main" is the first
   double sig_curr[bin[varPos]]; double sig_curr_err[bin[varPos]];
   double bkg_curr[bin[varPos]]; double bkg_curr_err[bin[varPos]];
   double sumBkgs[bin[varPos]]; double sumBkgs_err[bin[varPos]]; 
   vector<vector<double>> processes_bins; processes_bins.clear();
   //Loop over all samples
   vector<string> rootplas(samples, samples + sizeof(samples)/sizeof(samples[0]));
   int samplesSize = int(sizeof(samples)/sizeof(samples[0]));
   for(int r=0; r<samplesSize; r++){
    TFile* f = Call_TFile(rootplas[r]);
    TTree* tree; f->GetObject(trees[t].c_str(),tree);
    //Get events
    TH1F *hist = get_th1f("hist",variable,varPos); 
    TH1F *hist_err = get_th1f("hist_err",variable,varPos); 
    TH1F *hist_err2 = get_th1f("hist_err2",variable,varPos); 
    get_evt(tree,variable,r,varPos,allWeights,ws,isNotDataDriven,hist,hist_err,hist_err2);
    //cout<<t<<" "<<ws<<" "<<rootplas[r]<<endl;
    //bins
    vector<double> bins; bins.clear();
    for(int b=0; b<bin[varPos]; b++){
     //Simulation sig
     if(r<numSigs){
      if(r==0){sig_curr[b] = 0; sig_curr_err[b] = 0;}
      sig_curr[b] += hist->GetBinContent(b+1); 
      if(hist_err->GetBinContent(b+1)>0){sig_curr_err[b] += hist_err->GetBinContent(b+1);}else{sig_curr_err[b] += 0;}
      if(r==0){//The number must equal the position of the signal samples in "samples" of Declare Constants
       if(trees[t]=="Events" && weights_sys[ws]=="main"){LQLQ1p5->SetBinContent(b+1,sig_curr[b]); LQLQ1p5->SetBinError(b+1,sqrt(sig_curr_err[b]));}
       else{bins.push_back(fabs(LQLQ1p5->GetBinContent(b+1)-sig_curr[b]));} //Note that if you do not require fabs, the difference can be negative, hence Sum_bins(fabs(diff)) != hist->Integral-Sys->Integral
       //else{bins.push_back(sig_curr[b]);}
       sig_curr[b] = 0; sig_curr_err[b] = 0;
      } 
     }
     //Simulation bkg     
     if(numSigs<=r && r<numSigs+numTTbar+numWJets+numOthers){
      if(r==numSigs){bkg_curr[b] = 0; bkg_curr_err[b] = 0; sumBkgs[b] = 0; sumBkgs_err[b] = 0;}
      bkg_curr[b] += hist->GetBinContent(b+1);
      if(hist_err->GetBinContent(b+1)>0){bkg_curr_err[b] += hist_err->GetBinContent(b+1);}else{bkg_curr_err[b] += 0;}
      if(r==numSigs+numTTbar-1){
       if(trees[t]=="Events" && weights_sys[ws]=="main"){TTbar->SetBinContent(b+1,bkg_curr[b]); TTbar->SetBinError(b+1,sqrt(bkg_curr_err[b]));}
       else{bins.push_back(fabs(TTbar->GetBinContent(b+1)-bkg_curr[b]));}
       //else{bins.push_back(bkg_curr[b]);}
       bkg_curr[b] = 0; bkg_curr_err[b] = 0;
      }
      if(r==numSigs+numTTbar+numWJets-1){
       if(trees[t]=="Events" && weights_sys[ws]=="main"){WJets->SetBinContent(b+1,bkg_curr[b]); WJets->SetBinError(b+1,sqrt(bkg_curr_err[b]));}
       else{bins.push_back(fabs(WJets->GetBinContent(b+1)-bkg_curr[b]));} 
       //else{bins.push_back(bkg_curr[b]);}
       bkg_curr[b] = 0; bkg_curr_err[b] = 0;
      }
      if(r==numSigs+numTTbar+numWJets+numOthers-1){
       if(trees[t]=="Events" && weights_sys[ws]=="main"){Others->SetBinContent(b+1,bkg_curr[b]); Others->SetBinError(b+1,sqrt(bkg_curr_err[b]));}
       else{bins.push_back(fabs(Others->GetBinContent(b+1)-bkg_curr[b]));} 
       //else{bins.push_back(bkg_curr[b]);}
       bkg_curr[b] = 0; bkg_curr_err[b] = 0; //This line is not needed, but I leave it for symmetry
      }
      sumBkgs[b] += hist->GetBinContent(b+1);
      if(hist_err->GetBinContent(b+1)>0){sumBkgs_err[b] += hist_err->GetBinContent(b+1);}else{bkg_curr_err[b] += 0;}  
     }
     //Data
     if(r==numSigs+numTTbar+numWJets+numOthers){
      if(!isNotDataDriven){
       if(trees[t]=="Events" && weights_sys[ws]=="main"){
       dataDriven->SetBinContent(b+1,hist->GetBinContent(b+1)-sumBkgs[b]);
       double den = hist->GetBinContent(b+1); if(den==0) den=1;
       dataDriven->SetBinError(b+1,
       sqrt(//Remember that for multijet estimation: central value = (Data-MC)*Corr, error = sqrt(dData2*Corr2+dMC2*Corr2+dCorr2*(Data-MC)2) 
       hist_err->GetBinContent(b+1)+ //corresponds to dData2*Corr2
       sumBkgs_err[b]+ //corresponds to dMC2*Corr2
       (hist_err2->GetBinContent(b+1)/den) * pow(hist->GetBinContent(b+1)-sumBkgs[b],2) //corresponds to dCorr2*(Data-MC)
       ));}
       //if(trees[t]=="Events" && weights_sys[ws]=="main"){dataDriven->SetBinContent(b+1,hist->GetBinContent(b+1)-sumBkgs[b]); dataDriven->SetBinError(b+1,0);} 
       else{bins.push_back(0);}//fabs(hist->GetBinContent(b+1)-sumBkgs[b]));} //No syst on data-driven bkg otherwise fabs(hist->GetBinContent(b+1)-sumBkgs[b])-centralValu?
      }
      if(isNotDataDriven && !nodata) if(trees[t]=="Events" && weights_sys[ws]=="main") data->SetBinContent(b+1,hist->GetBinContent(b+1)); 
     }
    }//End bins
    delete hist; delete hist_err;
    if(addsys && ((trees[t]=="Events" && weights_sys[ws]!="main") || (trees[t]!="Events" && weights_sys[ws]=="main"))){
     if((r<numSigs || r==numSigs+numTTbar-1 || r==numSigs+numTTbar+numWJets-1 || r==numSigs+numTTbar+numWJets+numOthers-1) && isNotDataDriven) processes_bins.push_back(bins);
     if(r==numSigs+numTTbar+numWJets+numOthers && !isNotDataDriven) systematics_processes_bins[systematic].push_back(bins);
    }
    delete f;
   }//Loop over all samples
   if(addsys && isNotDataDriven && ((trees[t]=="Events" && weights_sys[ws]!="main") || (trees[t]!="Events" && weights_sys[ws]=="main"))) systematics_processes_bins.push_back(processes_bins);
   if(addsys && ((trees[t]=="Events" && weights_sys[ws]!="main") || (trees[t]!="Events" && weights_sys[ws]=="main"))) systematic++;
  }//For the systematics related to variations of the weights
 }//For the systematics related to variations that require re-running the full analysis and thus have different trees
}
void get_evt(TTree* tree,string variable,int samplePos,int varPos,vector<vector<string>> allWeights,int ws,bool isNotDataDriven,TH1F *hist,TH1F *hist_err,TH1F *hist_err2){
 //The variable
 double var; TBranch *b_var = 0; tree->SetBranchAddress(variable.c_str(),&var,&b_var); 
 //Weights
 double genWeight; TBranch *b_genWeight = 0; tree->SetBranchAddress("genWeight",&genWeight,&b_genWeight);
 double weight0; TBranch *b_weight0 = 0; tree->SetBranchAddress(allWeights[ws][0].c_str(),&weight0,&b_weight0); 
 double weight1; TBranch *b_weight1 = 0; tree->SetBranchAddress(allWeights[ws][1].c_str(),&weight1,&b_weight1); 
 double weight2; TBranch *b_weight2 = 0; tree->SetBranchAddress(allWeights[ws][2].c_str(),&weight2,&b_weight2); 
 double weight3; TBranch *b_weight3 = 0; tree->SetBranchAddress(allWeights[ws][3].c_str(),&weight3,&b_weight3); 
 double weight4; TBranch *b_weight4 = 0; tree->SetBranchAddress(allWeights[ws][4].c_str(),&weight4,&b_weight4); 
 double weight5; TBranch *b_weight5 = 0; tree->SetBranchAddress(allWeights[ws][5].c_str(),&weight5,&b_weight5); 
 double weight6; TBranch *b_weight6 = 0; tree->SetBranchAddress(allWeights[ws][6].c_str(),&weight6,&b_weight6); //Increase/descrese based on the weights you use in the analysis
 //Selection
 double tauOrigin; TBranch *b_tauOrigin = 0; tree->SetBranchAddress("tauOrigin",&tauOrigin,&b_tauOrigin); 
 double tau_VTight; TBranch *b_tau_VTight = 0; tree->SetBranchAddress("tau_VTight",&tau_VTight,&b_tau_VTight); 
 double tau_pt; TBranch *b_tau_pt = 0; tree->SetBranchAddress("tau_pt",&tau_pt,&b_tau_pt); 
 double tau_eta; TBranch *b_tau_eta = 0; tree->SetBranchAddress("tau_eta",&tau_eta,&b_tau_eta); 
 double tauJet_pt; TBranch *b_tauJet_pt = 0; tree->SetBranchAddress("tauJet_pt",&tauJet_pt,&b_tauJet_pt); 
 double tauJet_eta; TBranch *b_tauJet_eta = 0; tree->SetBranchAddress("tauJet_eta",&tauJet_eta,&b_tauJet_eta); 
 double tau_idMVAoldDM2017v2; TBranch *b_tau_idMVAoldDM2017v2 = 0; tree->SetBranchAddress("tau_idMVAoldDM2017v2",&tau_idMVAoldDM2017v2,&b_tau_idMVAoldDM2017v2);
 double HT; TBranch *b_HT = 0; tree->SetBranchAddress("HT",&HT,&b_HT);
 double MHT; TBranch *b_MHT = 0; tree->SetBranchAddress("MHT",&MHT,&b_MHT);
 double MET_pt; TBranch *b_MET_pt = 0; tree->SetBranchAddress("MET_pt",&MET_pt,&b_MET_pt);
 double massT; TBranch *b_massT = 0; tree->SetBranchAddress("massT",&massT,&b_massT);
 double category; TBranch *b_category = 0; tree->SetBranchAddress("category",&category,&b_category);
 double numBjetsL; TBranch *b_numBjetsL = 0; tree->SetBranchAddress("numBjetsL",&numBjetsL,&b_numBjetsL);
 //double numBjetsL; TBranch *b_numBjetsL = 0; tree->SetBranchAddress("numBjetsDeepFlavourL",&numBjetsL,&b_numBjetsL);
 for(int e=0; e<tree->GetEntries(); e++){
  Long64_t tentry = tree->LoadTree(e); 
  //The variable
  b_var->GetEntry(tentry);
  //Weights
  b_genWeight->GetEntry(tentry);
  b_weight0->GetEntry(tentry);
  b_weight1->GetEntry(tentry);
  b_weight2->GetEntry(tentry);
  b_weight3->GetEntry(tentry);
  b_weight4->GetEntry(tentry);
  b_weight5->GetEntry(tentry);
  b_weight6->GetEntry(tentry); //Increase/descrese based on the weights you use in the analysis
  //Selection
  b_tauOrigin->GetEntry(tentry);
  b_tau_VTight->GetEntry(tentry);
  b_tau_pt->GetEntry(tentry);
  b_tau_eta->GetEntry(tentry);
  b_tauJet_pt->GetEntry(tentry);
  b_tauJet_eta->GetEntry(tentry);
  b_tau_idMVAoldDM2017v2->GetEntry(tentry);
  b_HT->GetEntry(tentry);
  b_MHT->GetEntry(tentry);
  b_MET_pt->GetEntry(tentry);
  b_massT->GetEntry(tentry);
  b_category->GetEntry(tentry);
  b_numBjetsL->GetEntry(tentry);
  if(!(HT>300 && MET_pt>200 && category>0 && numBjetsL>0 && MHT>=200 && massT>=300)) continue; //massT>=300
  //if(numSigs<=samplePos && samplePos<numSigs+numTTbar+numWJets+numOthers){
  if(samplePos>=numSigs){
   if(isNotDataDriven)  if(!(tauOrigin!=0 && tau_idMVAoldDM2017v2>=tauTWP)) continue;
   if(!isNotDataDriven) if(!(tauOrigin!=0 && tauLWP<=tau_idMVAoldDM2017v2 && tau_idMVAoldDM2017v2<tauTWP))  continue; 
  }else{
   if(!(tau_idMVAoldDM2017v2>=tauTWP)) continue;
  }
  //Weights
  double weight = weight0*weight1*weight2*weight3*weight4*weight5*weight6*lumiWeights[samplePos]; //Increase/descrese based on the weights you use in the analysis //lumiWeights must be set to 1 for data
  if(numSigs<=samplePos && samplePos<numTTbar) weight = weight*SF_ttbar; //AS 2018: 0.9
  if(numSigs+numTTbar<=samplePos && samplePos<numSigs+numTTbar+numWJets) weight = weight*SF_WJets;//AS 2018: 1.06
  double weight2 = weight;
  if(!isNotDataDriven){//Need to apply the correctionFactor (tight-to-loose ratio) to get the estimation in the signal region 
   double correctionFactor = 1;
   double correctionFactorErr = 1;
   get_correctionFactor(tauJet_pt,tauJet_eta,correctionFactor,correctionFactorErr);
   weight = weight*correctionFactor;      
   weight2 = weight2*correctionFactor*correctionFactorErr;       
  }
  if(inRange[varPos]<var && var<endRange[varPos]) {hist->Fill(var,weight*genWeight); hist_err->Fill(var,weight*weight*genWeight); hist_err2->Fill(var,weight2*weight2*genWeight);};
  if(var>=endRange[varPos])                       {hist->Fill(0.99*endRange[varPos],weight*genWeight); hist_err->Fill(0.99*endRange[varPos],weight*weight*genWeight); hist_err2->Fill(0.99*endRange[varPos],weight2*weight2*genWeight);};
  if(var<=inRange[varPos])                        {hist->Fill(1.01*inRange[varPos],weight*genWeight); hist_err->Fill(1.01*inRange[varPos],weight*weight*genWeight); hist_err2->Fill(1.01*inRange[varPos],weight2*weight2*genWeight); };
 } 
}
void get_correctionFactor(double pt,double eta, double& correctionFactor, double& correctionFactorErr){
 //FakeRate_TauDzVeryTight_11June
 if(taskFakaRate=="FakeRate_TauDzVeryTight_11June"){
  if(year=="2018/"){
   if(20<=pt && pt<30 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.231959; correctionFactorErr = 0.0323941;}
   if(20<=pt && pt<30 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.17343; correctionFactorErr = 0.0514471;}
   if(30<=pt && pt<50 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.101597; correctionFactorErr = 0.00591383;}
   if(30<=pt && pt<50 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.116241; correctionFactorErr = 0.00860513;}
   if(50<=pt && pt<75 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.0951752; correctionFactorErr = 0.00650725;}
   if(50<=pt && pt<75 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.0827091; correctionFactorErr = 0.00777603;}
   if(75<=pt && pt<100 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.0698492; correctionFactorErr = 0.00778159;}
   if(75<=pt && pt<100 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.120223; correctionFactorErr = 0.0141419;}
   if(100<=pt && pt<125 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.0793583; correctionFactorErr = 0.00995513;}
   if(100<=pt && pt<125 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.0937145; correctionFactorErr = 0.0161296;}
   if(125<=pt && pt<150 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.0803109; correctionFactorErr = 0.0124379;}
   if(125<=pt && pt<150 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.061372; correctionFactorErr = 0.0161316;}
   if(150<=pt && pt<200 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.0709516; correctionFactorErr = 0.0122117;}
   if(150<=pt && pt<200 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.106217; correctionFactorErr = 0.0222711;}
   if(200<=pt && pt<99999 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.0406733; correctionFactorErr = 2*0.0138033;}
   if(200<=pt && pt<99999 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.0197828; correctionFactorErr = 2*0.0166836;}
  }
  if(year=="2017/"){
   if(20<=pt && pt<30 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.231956; correctionFactorErr = 0.034694;}
   if(20<=pt && pt<30 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.208139; correctionFactorErr = 0.0625358;}
   if(30<=pt && pt<50 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.0977576; correctionFactorErr = 0.00627213;}
   if(30<=pt && pt<50 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.138596; correctionFactorErr = 0.00952466;}
   if(50<=pt && pt<75 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.0998962; correctionFactorErr = 0.00732063;}
   if(50<=pt && pt<75 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.0920162; correctionFactorErr = 0.00814956;}
   if(75<=pt && pt<100 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.0828248; correctionFactorErr = 0.00960107;}
   if(75<=pt && pt<100 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.091285; correctionFactorErr = 0.0119482;}
   if(100<=pt && pt<125 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.06446; correctionFactorErr = 0.0105695;}
   if(100<=pt && pt<125 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.0886821; correctionFactorErr = 0.0154916;}
   if(125<=pt && pt<150 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.0450531; correctionFactorErr = 0.0126201;}
   if(125<=pt && pt<150 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.0485708; correctionFactorErr = 0.0143003;}
   if(150<=pt && pt<200 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.0563975; correctionFactorErr = 0.0145405;}
   if(150<=pt && pt<200 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.0502956; correctionFactorErr = 0.0179726;}
   if(200<=pt && pt<99999 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.0640188; correctionFactorErr = 2*0.019536;}
   if(200<=pt && pt<99999 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.0454728; correctionFactorErr = 2*0.0231876;}
  }
  if(year=="2016/"){
   if(20<=pt && pt<30 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.272356; correctionFactorErr = 0.0439339;}
   if(20<=pt && pt<30 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.274778; correctionFactorErr = 0.057322;}
   if(30<=pt && pt<50 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.110239; correctionFactorErr = 0.0080686;}
   if(30<=pt && pt<50 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.108887; correctionFactorErr = 0.00893467;}
   if(50<=pt && pt<75 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.0954786; correctionFactorErr = 0.00931286;}
   if(50<=pt && pt<75 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.081865; correctionFactorErr = 0.00963862;}
   if(75<=pt && pt<100 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.0924338; correctionFactorErr = 0.0124042;}
   if(75<=pt && pt<100 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.0762162; correctionFactorErr = 0.0148147;}
   if(100<=pt && pt<125 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.0627475; correctionFactorErr = 0.0141631;}
   if(100<=pt && pt<125 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.0704183; correctionFactorErr = 0.0169218;}
   if(125<=pt && pt<150 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.0251703; correctionFactorErr = 0.0164262;}
   if(125<=pt && pt<150 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.056338; correctionFactorErr = 0.0223641;}
   if(150<=pt && pt<200 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.0612516; correctionFactorErr = 0.0213356;}
   if(150<=pt && pt<200 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.0432444; correctionFactorErr = 0.0312719;}
   if(200<=pt && pt<99999 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.028538; correctionFactorErr = 2*0.0250792;}
   if(200<=pt && pt<99999 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.0607993; correctionFactorErr = 2*0.0298792;}
  }
 }
 //FakeRate_TauDzTight_11June
 if(taskFakaRate=="FakeRate_TauDzTight_11June"){
  if(year=="2018/"){
   if(20<=pt && pt<30 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.384463; correctionFactorErr = 0.046216;}
   if(20<=pt && pt<30 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.212627; correctionFactorErr = 0.0591785;}
   if(30<=pt && pt<50 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.186384; correctionFactorErr = 0.00828442;}
   if(30<=pt && pt<50 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.216723; correctionFactorErr = 0.0126841;}
   if(50<=pt && pt<75 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.163165; correctionFactorErr = 0.00865988;}
   if(50<=pt && pt<75 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.177778; correctionFactorErr = 0.0119662;}
   if(75<=pt && pt<100 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.130807; correctionFactorErr = 0.0103382;}
   if(75<=pt && pt<100 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.206939; correctionFactorErr = 0.0195462;}
   if(100<=pt && pt<125 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.154628; correctionFactorErr = 0.0136218;}
   if(100<=pt && pt<125 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.167702; correctionFactorErr = 0.0224099;}
   if(125<=pt && pt<150 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.143974; correctionFactorErr = 0.0165819;}
   if(125<=pt && pt<150 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.124756; correctionFactorErr = 0.0229192;}
   if(150<=pt && pt<200 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.115136; correctionFactorErr = 0.0152147;}
   if(150<=pt && pt<200 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.170572; correctionFactorErr = 0.0298086;}
   if(200<=pt && pt<99999 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.107947; correctionFactorErr = 2*0.0195775;}
   if(200<=pt && pt<99999 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.0858721; correctionFactorErr = 2*0.0293121;}
  }
  if(year=="2017/"){
   if(20<=pt && pt<30 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.349874; correctionFactorErr = 0.0460606;}
   if(20<=pt && pt<30 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.419726; correctionFactorErr = 0.103208;}
   if(30<=pt && pt<50 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.182696; correctionFactorErr = 0.00889245;}
   if(30<=pt && pt<50 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.24187; correctionFactorErr = 0.013651;}
   if(50<=pt && pt<75 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.171069; correctionFactorErr = 0.00975871;}
   if(50<=pt && pt<75 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.184304; correctionFactorErr = 0.0122581;}
   if(75<=pt && pt<100 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.155061; correctionFactorErr = 0.0129299;}
   if(75<=pt && pt<100 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.160235; correctionFactorErr = 0.0164956;}
   if(100<=pt && pt<125 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.114472; correctionFactorErr = 0.0135327;}
   if(100<=pt && pt<125 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.163792; correctionFactorErr = 0.021734;}
   if(125<=pt && pt<150 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.117996; correctionFactorErr = 0.0182121;}
   if(125<=pt && pt<150 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.113936; correctionFactorErr = 0.0223083;}
   if(150<=pt && pt<200 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.102333; correctionFactorErr = 0.0183673;}
   if(150<=pt && pt<200 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.0927745; correctionFactorErr = 0.024087;}
   if(200<=pt && pt<99999 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.115575; correctionFactorErr = 2*0.0247331;}
   if(200<=pt && pt<99999 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.169217; correctionFactorErr = 2*0.0450458;}
  }
  if(year=="2016/"){
   if(20<=pt && pt<30 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.388387; correctionFactorErr = 0.0551501;}
   if(20<=pt && pt<30 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.379596; correctionFactorErr = 0.0729659;}
   if(30<=pt && pt<50 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.186552; correctionFactorErr = 0.0107049;}
   if(30<=pt && pt<50 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.219706; correctionFactorErr = 0.0139297;}
   if(50<=pt && pt<75 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.161334; correctionFactorErr = 0.0122384;}
   if(50<=pt && pt<75 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.154417; correctionFactorErr = 0.0137601;}
   if(75<=pt && pt<100 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.158319; correctionFactorErr = 0.0160957;}
   if(75<=pt && pt<100 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.132492; correctionFactorErr = 0.0192751;}
   if(100<=pt && pt<125 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.105931; correctionFactorErr = 0.0181615;}
   if(100<=pt && pt<125 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.136099; correctionFactorErr = 0.0237036;}
   if(125<=pt && pt<150 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.0754625; correctionFactorErr = 0.0218256;}
   if(125<=pt && pt<150 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.146429; correctionFactorErr = 0.0351001;}
   if(150<=pt && pt<200 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.0966569; correctionFactorErr = 0.0250752;}
   if(150<=pt && pt<200 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.0918653; correctionFactorErr = 0.0385398;}
   if(200<=pt && pt<99999 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.0777944; correctionFactorErr = 2*0.0312927;}
   if(200<=pt && pt<99999 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.144769; correctionFactorErr = 2*0.0462979;}
  }
 }
 //FakeRate_TauDzMedium
 if(taskFakaRate=="FakeRate_TauDzMedium"){
  if(year=="2018/"){
   if(20<=pt && pt<30 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.612194; correctionFactorErr = 0.0673723;}
   if(20<=pt && pt<30 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.491747; correctionFactorErr = 0.109124;}
   if(30<=pt && pt<50 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.352891; correctionFactorErr = 0.0126566;}
   if(30<=pt && pt<50 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.426547; correctionFactorErr = 0.0207169;}
   if(50<=pt && pt<75 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.297275; correctionFactorErr = 0.0124713;}
   if(50<=pt && pt<75 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.349929; correctionFactorErr = 0.0189548;}
   if(75<=pt && pt<100 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.264317; correctionFactorErr = 0.0153147;}
   if(75<=pt && pt<100 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.375106; correctionFactorErr = 0.0292286;}
   if(100<=pt && pt<125 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.283762; correctionFactorErr = 0.0197316;}
   if(100<=pt && pt<125 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.348337; correctionFactorErr = 0.0363046;}
   if(125<=pt && pt<150 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.257694; correctionFactorErr = 0.0231412;}
   if(125<=pt && pt<150 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.282289; correctionFactorErr = 0.0372872;}
   if(150<=pt && pt<200 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.216827; correctionFactorErr = 0.0215037;}
   if(150<=pt && pt<200 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.315805; correctionFactorErr = 0.0450562;}
   if(200<=pt && pt<99999 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.21051; correctionFactorErr = 2*0.0275126;}
   if(200<=pt && pt<99999 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.167535; correctionFactorErr = 2*0.0422742;}
  }
  if(year=="2017/"){
   if(20<=pt && pt<30 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.597599; correctionFactorErr = 0.0697801;}
   if(20<=pt && pt<30 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.723742; correctionFactorErr = 0.163367;}
   if(30<=pt && pt<50 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.35758; correctionFactorErr = 0.0138136;}
   if(30<=pt && pt<50 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.471015; correctionFactorErr = 0.0223426;}
   if(50<=pt && pt<75 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.316429; correctionFactorErr = 0.0143377;}
   if(50<=pt && pt<75 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.385763; correctionFactorErr = 0.020389;}
   if(75<=pt && pt<100 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.276655; correctionFactorErr = 0.0180857;}
   if(75<=pt && pt<100 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.318388; correctionFactorErr = 0.025814;}
   if(100<=pt && pt<125 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.243509; correctionFactorErr = 0.0202106;}
   if(100<=pt && pt<125 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.321394; correctionFactorErr = 0.0337839;}
   if(125<=pt && pt<150 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.238986; correctionFactorErr = 0.0265955;}
   if(125<=pt && pt<150 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.291515; correctionFactorErr = 0.0396885;}
   if(150<=pt && pt<200 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.196125; correctionFactorErr = 0.0253629;}
   if(150<=pt && pt<200 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.233383; correctionFactorErr = 0.0401952;}
   if(200<=pt && pt<99999 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.201077; correctionFactorErr = 2*0.0326876;}
   if(200<=pt && pt<99999 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.297502; correctionFactorErr = 2*0.0653472;}
  }
  if(year=="2016/"){
   if(20<=pt && pt<30 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.659872; correctionFactorErr = 0.0824035;}
   if(20<=pt && pt<30 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.662921; correctionFactorErr = 0.115492;}
   if(30<=pt && pt<50 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.364462; correctionFactorErr = 0.0164232;}
   if(30<=pt && pt<50 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.43313; correctionFactorErr = 0.0225782;}
   if(50<=pt && pt<75 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.323255; correctionFactorErr = 0.0183188;}
   if(50<=pt && pt<75 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.325528; correctionFactorErr = 0.0224169;}
   if(75<=pt && pt<100 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.28703; correctionFactorErr = 0.0222843;}
   if(75<=pt && pt<100 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.291367; correctionFactorErr = 0.0306574;}
   if(100<=pt && pt<125 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.235238; correctionFactorErr = 0.0258236;}
   if(100<=pt && pt<125 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.291157; correctionFactorErr = 0.0371919;}
   if(125<=pt && pt<150 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.168372; correctionFactorErr = 0.0299254;}
   if(125<=pt && pt<150 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.356728; correctionFactorErr = 0.061398;}
   if(150<=pt && pt<200 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.23426; correctionFactorErr = 0.0370147;}
   if(150<=pt && pt<200 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.288519; correctionFactorErr = 0.0659013;}
   if(200<=pt && pt<99999 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.159493; correctionFactorErr = 0.0420086;}
   if(200<=pt && pt<99999 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.275852; correctionFactorErr = 0.0687521;}
  }
 }
 //FakeRate_11June
 if(taskFakaRate=="FakeRate_11June"){
  //2018
  if(year=="2018/"){
   if(20<=pt && pt<30 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.607204; correctionFactorErr = 0.0394193;}
   if(20<=pt && pt<30 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.598916; correctionFactorErr = 0.0578504;}
   if(30<=pt && pt<50 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.372075; correctionFactorErr = 0.0123128;}
   if(30<=pt && pt<50 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.439282; correctionFactorErr = 0.019534;}
   if(50<=pt && pt<75 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.303194; correctionFactorErr = 0.012293;}
   if(50<=pt && pt<75 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.357298; correctionFactorErr = 0.0183351;}
   if(75<=pt && pt<100 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.271448; correctionFactorErr = 0.0152426;}
   if(75<=pt && pt<100 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.355161; correctionFactorErr = 0.0261637;}
   if(100<=pt && pt<125 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.288414; correctionFactorErr = 0.019559;}
   if(100<=pt && pt<125 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.351479; correctionFactorErr = 0.0338169;}
   if(125<=pt && pt<150 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.257414; correctionFactorErr = 0.0227542;}
   if(125<=pt && pt<150 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.28913; correctionFactorErr = 0.035595;}
   if(150<=pt && pt<200 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.225184; correctionFactorErr = 0.0215728;}
   if(150<=pt && pt<200 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.297512; correctionFactorErr = 0.0393667;}
   if(200<=pt && pt<99999 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.219454; correctionFactorErr = 2*0.0273746;}
   if(200<=pt && pt<99999 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.156158; correctionFactorErr = 2*0.0365226;}
  }
  //2017
  if(year=="2017/"){
   if(20<=pt && pt<30 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.549328; correctionFactorErr = 0.0380745;}
   if(20<=pt && pt<30 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.588489; correctionFactorErr = 0.0577725;}
   if(30<=pt && pt<50 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.377787; correctionFactorErr = 0.0134642;}
   if(30<=pt && pt<50 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.474257; correctionFactorErr = 0.0206211;}
   if(50<=pt && pt<75 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.316812; correctionFactorErr = 0.0139399;}
   if(50<=pt && pt<75 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.389158; correctionFactorErr = 0.0194382;}
   if(75<=pt && pt<100 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.282531; correctionFactorErr = 0.0178803;}
   if(75<=pt && pt<100 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.315628; correctionFactorErr = 0.0246354;}
   if(100<=pt && pt<125 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.246528; correctionFactorErr = 0.019977;}
   if(100<=pt && pt<125 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.310114; correctionFactorErr = 0.0310504;}
   if(125<=pt && pt<150 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.24042; correctionFactorErr = 0.0260434;}
   if(125<=pt && pt<150 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.310167; correctionFactorErr = 0.039271;}
   if(150<=pt && pt<200 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.201073; correctionFactorErr = 0.0251941;}
   if(150<=pt && pt<200 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.22665; correctionFactorErr = 0.0357988;}
   if(200<=pt && pt<99999 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.203921; correctionFactorErr = 2*0.0318314;}
   if(200<=pt && pt<99999 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.287472; correctionFactorErr = 2*0.0571165;}
  }
  //2016
  if(year=="2016/"){
   if(20<=pt && pt<30 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.608364; correctionFactorErr = 0.0522778;}
   if(20<=pt && pt<30 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.617109; correctionFactorErr = 0.0681816;}
   if(30<=pt && pt<50 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.366523; correctionFactorErr = 0.0157763;}
   if(30<=pt && pt<50 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.425979; correctionFactorErr = 0.0211458;}
   if(50<=pt && pt<75 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.33103; correctionFactorErr = 0.0181138;}
   if(50<=pt && pt<75 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.310473; correctionFactorErr = 0.0207007;}
   if(75<=pt && pt<100 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.267491; correctionFactorErr = 0.0217331;}
   if(75<=pt && pt<100 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.285811; correctionFactorErr = 0.0280977;}
   if(100<=pt && pt<125 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.232508; correctionFactorErr = 0.024631;}
   if(100<=pt && pt<125 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.304538; correctionFactorErr = 0.035018;}
   if(125<=pt && pt<150 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.196688; correctionFactorErr = 0.0302337;}
   if(125<=pt && pt<150 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.359273; correctionFactorErr = 0.0560361;}
   if(150<=pt && pt<200 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.241109; correctionFactorErr = 0.0350307;}
   if(150<=pt && pt<200 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.244058; correctionFactorErr = 0.0560718;}
   if(200<=pt && pt<99999 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.170436; correctionFactorErr = 2*0.0403612;}
   if(200<=pt && pt<99999 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.259842; correctionFactorErr = 2*0.0576371;}
  }
 }
 /*2018 20May
 if(20<=pt && pt<30 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.604433; correctionFactorErr = 0.0394458;}
 if(20<=pt && pt<30 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.603559; correctionFactorErr = 0.0581036;}
 if(30<=pt && pt<50 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.370756; correctionFactorErr = 0.0123907;}
 if(30<=pt && pt<50 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.438897; correctionFactorErr = 0.0195407;}
 if(50<=pt && pt<75 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.305407; correctionFactorErr = 0.0124194;}
 if(50<=pt && pt<75 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.355433; correctionFactorErr = 0.0183337;}
 if(75<=pt && pt<100 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.269206; correctionFactorErr = 0.0155173;}
 if(75<=pt && pt<100 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.35543; correctionFactorErr = 0.0264165;}
 if(100<=pt && pt<125 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.287908; correctionFactorErr = 0.0198263;}
 if(100<=pt && pt<125 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.346645; correctionFactorErr = 0.0339317;}
 if(125<=pt && pt<150 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.260362; correctionFactorErr = 0.0231485;}
 if(125<=pt && pt<150 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.28792; correctionFactorErr = 0.0357861;}
 if(150<=pt && pt<200 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.224416; correctionFactorErr = 0.0220891;}
 if(150<=pt && pt<200 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.300116; correctionFactorErr = 0.0396602;}
 if(200<=pt && pt<99999 && 0.0<=fabs(eta) && fabs(eta)<1.5){correctionFactor = 0.228877; correctionFactorErr = 2*0.0279145;}
 if(200<=pt && pt<99999 && 1.5<=fabs(eta) && fabs(eta)<2.3){correctionFactor = 0.153436; correctionFactorErr = 2*0.0375806;}
 */
 //2018 Aniello's
 /*
 if(pt>= 20  && pt<  30   && fabs(eta)>=0.0 && fabs(eta)<1.5){correctionFactor = 0.596723; correctionFactorErr = 0.0127484;}
 if(pt>= 20  && pt<  30   && fabs(eta)>=1.5 && fabs(eta)<2.3){correctionFactor = 0.622164; correctionFactorErr = 0.0194105;}

 if(pt>= 30  && pt<  50   && fabs(eta)>=0.0 && fabs(eta)<1.5){correctionFactor = 0.380575; correctionFactorErr = 0.0053432;} 
 if(pt>= 30  && pt<  50   && fabs(eta)>=1.5 && fabs(eta)<2.3){correctionFactor = 0.44919;  correctionFactorErr = 0.00785651;}

 if(pt>= 50  && pt<  75   && fabs(eta)>=0.0 && fabs(eta)<1.5){correctionFactor = 0.312026; correctionFactorErr = 0.00585096;} 
 if(pt>= 50  && pt<  75   && fabs(eta)>=1.5 && fabs(eta)<2.3){correctionFactor = 0.360375; correctionFactorErr = 0.00825616;}

 if(pt>= 75  && pt< 100   && fabs(eta)>=0.0 && fabs(eta)<1.5){correctionFactor = 0.284702; correctionFactorErr = 0.00747927;}
 if(pt>= 75  && pt< 100   && fabs(eta)>=1.5 && fabs(eta)<2.3){correctionFactor = 0.370173; correctionFactorErr = 0.0114268;}

 if(pt>=100  && pt< 125   && fabs(eta)>=0.0 && fabs(eta)<1.5){correctionFactor = 0.289263; correctionFactorErr = 0.00842112;}
 if(pt>=100  && pt< 125   && fabs(eta)>=1.5 && fabs(eta)<2.3){correctionFactor = 0.359481; correctionFactorErr = 0.0131306;}

 if(pt>=125  && pt< 150   && fabs(eta)>=0.0 && fabs(eta)<1.5){correctionFactor = 0.259364; correctionFactorErr = 0.00821405;}
 if(pt>=125  && pt< 150   && fabs(eta)>=1.5 && fabs(eta)<2.3){correctionFactor = 0.321478; correctionFactorErr = 0.01373;}

 if(pt>=150  && pt< 200   && fabs(eta)>=0.0 && fabs(eta)<1.5){correctionFactor = 0.259029; correctionFactorErr = 0.00697039;}
 if(pt>=150  && pt< 200   && fabs(eta)>=1.5 && fabs(eta)<2.3){correctionFactor = 0.335663; correctionFactorErr = 0.0121807;}

 if(pt>=200  && pt<99999  && fabs(eta)>=0.0 && fabs(eta)<1.5){correctionFactor = 0.293413; correctionFactorErr = 2*0.00940946;}
 if(pt>=200  && pt<99999  && fabs(eta)>=1.5 && fabs(eta)<2.3){correctionFactor = 0.255239; correctionFactorErr = 2*0.0158546;}
 */

}
/////
//   Print entries and errors and get total errors (stat. and sys.)
/////
void entries_errors(TH1F* LQLQ1p5,TH1F* TTbar,TH1F* WJets,TH1F* Others,TH1F* dataDrivenDD,TH1F* SumBkgs,TH1F* data,int varPos,vector<vector<vector<double>>> systematics_processes_bins,vector<double> &SumBkgs_errStatSysBins){
 //Print entries and stat. errors
 Double_t TTbErr = 0; Float_t TTbYield = TTbar->IntegralAndError(1,bin[varPos],TTbErr,"");
 Double_t WJeErr = 0; Float_t WJeYield = WJets->IntegralAndError(1,bin[varPos],WJeErr,"");
 Double_t FakErr = 0; Float_t FakYield = dataDrivenDD->IntegralAndError(1,bin[varPos],FakErr,"");
 Double_t OthErr = 0; Float_t OthYield = Others->IntegralAndError(1,bin[varPos],OthErr,"");
 Double_t SumBkgsErr = 0; Float_t SumBkgsYield = SumBkgs->IntegralAndError(1,bin[varPos],SumBkgsErr,"");
 Double_t datErr = 0; Float_t datYield = data->IntegralAndError(1,bin[varPos],datErr,"");
 Double_t LQLQ1p5Err = 0; Float_t LQLQ1p5Yield = LQLQ1p5->IntegralAndError(1,bin[varPos],LQLQ1p5Err,"");
 cout<<"TTbar     = "<<TTbar->Integral()<<" +/- "<<TTbErr<<endl;
 cout<<"WJets     = "<<WJets->Integral()<<" +/- "<<WJeErr<<endl;
 cout<<"Others    = "<<Others->Integral()<<" +/- "<<OthErr<<endl;
 cout<<"jet->tau  = "<<dataDrivenDD->Integral()<<" +/- "<<FakErr<<endl;
 cout<<"Total BKG = "<<SumBkgs->Integral()<<" +/- "<<SumBkgsErr<<endl;
 if(!nodata) cout<<"data      = "<<data->Integral()<<" +/- "<<datErr<<endl;
 cout<<"LQLQ1p5   = "<<LQLQ1p5->Integral()<<" +/- "<<LQLQ1p5Err<<endl;
 //Get tot sys (and prepare histos for combine)
 if(addsys){
  int systematics = int(systematics_processes_bins.size());
  int samples     = int(systematics_processes_bins[0].size());
  int bins        = int(systematics_processes_bins[0][0].size());
  //cout<<systematics<<" "<<samples<<" "<<bins<<endl;
  for(int r=numSigs; r<samples; r++){//We want only the bkg
   for(int ss=0; ss<systematics; ss = ss+2){//Because sys are Up and Down
    for(int bs=0; bs<bins; bs++){
     //Add stat err
     if(r==numSigs && ss==0) SumBkgs_errStatSysBins.push_back(pow(SumBkgs->GetBinError(bs+1),2)); //Just one time as it is SumBkgs already
     //if(r==numSigs && ss==0) SumBkgs_errStatSysBins.push_back(0); //Just one time as it is SumBkgs already
     //Add sys err
     double bin_maxUpDown = max(systematics_processes_bins[ss][r][bs],systematics_processes_bins[ss+1][r][bs]);
     bin_maxUpDown = pow(bin_maxUpDown,2);
     //cout<<r<<" "<<ss<<" "<<bs<<" "<<SumBkgs->GetBinContent(bs+1)<<" "<<systematics_processes_bins[ss][r][bs]<<" "<<systematics_processes_bins[ss+1][r][bs]<<" "<<bin_maxUpDown<<endl;
     SumBkgs_errStatSysBins[bs] += bin_maxUpDown; 
    }
   }
  }
  for(int bs=0; bs<bins; bs++){
   SumBkgs_errStatSysBins[bs] = sqrt(SumBkgs_errStatSysBins[bs]);
   //cout<<bs<<" "<<SumBkgs->GetBinContent(bs+1)<<" "<<SumBkgs->GetBinError(bs+1)<<" "<<SumBkgs_errStatSysBins[bs]<<endl;
  }
 }//addsys
}
/////
//   Draw the plots  
/////
void draw_plots(TH1F* LQLQ1p5,TH1F* TTbar,TH1F* WJets,TH1F* Others,TH1F* dataDrivenDD,TH1F* SumBkgs,TH1F* data,int varPos,vector<double> &SumBkgs_errStatSysBins){
 //Canvas
 TCanvas* c1 = new TCanvas("c1","c1",0,0,2500,2500);
 /////
 //   Bottom Pad
 ///// 
 TPad* c1_1 = get_pad("c1_1","c1_1",0.01,0.01,0.99,0.32,0.045,0.3,0.035,0.11);
 c1_1->Draw();
 c1_1->cd();
 //data
 TGraphAsymmErrors* gData = get_gData(data);
 //Ratios
 TH1F* ratioUnityStatErr = (TH1F*)SumBkgs->Clone();
 TH1F* ratioUnityStatSysErr = (TH1F*)SumBkgs->Clone();;
 TGraphAsymmErrors* ratioDataErr = get_ratios(varPos,gData,data,SumBkgs,SumBkgs_errStatSysBins,ratioUnityStatErr,ratioUnityStatSysErr);
 if(!nodata){
 ratioDataErr->Draw("AE0p");
  ratioUnityStatSysErr->Draw("E2same");
  ratioUnityStatErr->Draw("E2same");
  ratioDataErr->Draw("E0psame");
 }
 //Line
 TLine* line = new TLine(inRange[varPos],1,endRange[varPos],1); line->SetLineColor(2); line->SetLineWidth(2);
 line->Draw("same");
 c1->cd();
 /////
 //   Top pad
 /////
 TPad *c1_2 = get_pad("c1_2","c1_2",0.01,0.32,0.99,1.0,0.08,0.02,0.035,0.11);
 c1_2->Draw();
 c1_2->cd();
 //Stack plot
 THStack *hs = get_hstack(TTbar,WJets,dataDrivenDD,Others);
 //Signal
 LQLQ1p5->Draw("samehisto");
 //Data
 if(!nodata) gData->Draw("EP same");
 //Bkg
 SumBkgs->SetFillStyle(3005);
 SumBkgs->SetFillColor(12);
 SumBkgs->SetLineColor(12);
 SumBkgs->Draw("E2same");
 float maxy = get_maxy(data,SumBkgs);
 hs->SetMaximum(maxy);
 hs->SetMaximum(1000000);
 hs->SetMinimum(3);
 c1_2->SetLogy();
 //Legend
 TLegend *pl2 = new TLegend(0.53,0.56,0.95,0.91);
 pl2->SetTextSize(0.04);
 pl2->SetFillColor(0);
 TLegendEntry *ple2 = pl2->AddEntry(data, "data",  "L");
 ple2 = pl2->AddEntry(WJets, "WJets to l#nu",  "F");
 ple2 = pl2->AddEntry(TTbar, "top (t#bar{t}, t#bar{t}V, tZq, single-top)",  "F");
 ple2 = pl2->AddEntry(dataDrivenDD, "fake tau",  "F");
 ple2 = pl2->AddEntry(Others, "Others",  "F");
 ple2 = pl2->AddEntry(LQLQ1p5, "LQ, M=0.5TeV, pair, #sigma=1pb",  "L");
 pl2->Draw();
 /////
 //   Latex 
 /////
 float t = -1; float b = -1; float r = -1; float l = -1;
 get_marginsForLatex(t,b,r,l);
 TLatex latex;
 latex.SetNDC();
 latex.SetTextAngle(0);
 latex.SetTextColor(kBlack);
 latex.SetTextFont(42);
 latex.SetTextAlign(31);
 //Lumi text
 float lumiTextSize     = 0.6;
 latex.SetTextSize(lumiTextSize*t);
 //TString lumi_13TeV = "41.8 fb^{-1}"; TString lumi_8TeV = "19.7 fb^{-1}"; TString lumi_7TeV = "5.1 fb^{-1}"; 
 TString lumiText = "41.8 fb^{-1} (2017, 13 TeV)";
 latex.DrawLatex(1-r+0.06,0.94,lumiText);
 //CMS text
 //float cmsTextOffset = 0.1;  // only used in outOfFrame version
 float cmsTextFont = 61;  // default is helvetic-bold
 latex.SetTextFont(cmsTextFont);
 latex.SetTextAlign(11);
 float cmsTextSize = 0.75;
 latex.SetTextSize(cmsTextSize*t);
 TString cmsText = "CMS";
 latex.DrawLatex(l+0.01,0.94,cmsText);
 //Extra text
 float extraTextFont = 52;  // default is helvetica-italics
 latex.SetTextFont(extraTextFont);
 float extraOverCmsTextSize  = 0.76;
 float extraTextSize = extraOverCmsTextSize*cmsTextSize;
 latex.SetTextSize(extraTextSize*t);
 TString extraText   = "Preliminary";
 latex.DrawLatex(l+0.12, 0.94, extraText);
 float channelTextFont = 42;
 latex.SetTextFont(channelTextFont);
 float channelTextSize = 0.06;
 latex.SetTextSize(channelTextSize);
 /////
 //   Save plot
 /////
 cout<<"Finished "<<variables[varPos]<<endl;
 string saveas = string(variables[varPos])+".png";
 c1->SaveAs(saveas.c_str());
}
TGraphAsymmErrors* get_gData(TH1F* data){
 TGraphAsymmErrors *gData = new TGraphAsymmErrors(data);
 gData->SetLineWidth(2);
 gData->SetLineColor(1);
 gData->SetMarkerColor(1);
 gData->SetMarkerStyle(20);
 gData->SetMarkerSize(1.3);
 for(int m = 0; m<gData->GetN(); ++m){
  double alpha = 1 - 0.6827;
  int M = gData->GetY()[m];
  double L =  (M==0) ? 0  : (ROOT::Math::gamma_quantile(alpha/2,M,1.));
  double U =  ROOT::Math::gamma_quantile_c(alpha/2,M+1,1);
  gData->SetPointEYlow(m, M-L);
  gData->SetPointEYhigh(m, U-M);
  if(M==0){
   //ONLY FOR PLOT VISUALIZATION
   gData->SetPointEYlow( m, 0);
   gData->SetPointEYhigh(m, 0);
  }
 }
 return gData;
}
TGraphAsymmErrors* get_ratios(int varPos,TGraphAsymmErrors* gData,TH1F* data,TH1F* SumBkgs,vector<double> SumBkgs_errStatSysBins,TH1F* ratioUnityStatErr,TH1F* ratioUnityStatSysErr){
 Double_t x[bin[varPos]]; Double_t exl[bin[varPos]]; Double_t exh[bin[varPos]];
 Double_t y[bin[varPos]]; Double_t eyl[bin[varPos]]; Double_t eyh[bin[varPos]];
 //ratioUnityErr
 ratioUnityStatErr->SetFillStyle(3001);
 ratioUnityStatErr->SetFillColor(4);
 ratioUnityStatErr->SetLineColor(4);
 ratioUnityStatErr->SetMarkerSize(0);
 ratioUnityStatSysErr->SetFillStyle(3001);
 ratioUnityStatSysErr->SetFillColor(7);
 ratioUnityStatSysErr->SetLineColor(7);
 ratioUnityStatSysErr->SetMarkerSize(0);
 for(int m=0; m<SumBkgs->GetNbinsX(); m++){
  x[m]   = inRange[varPos]+m*(endRange[varPos]-inRange[varPos])/bin[varPos]+(endRange[varPos]-inRange[varPos])/(2*bin[varPos]);
  exl[m] = (endRange[varPos]-inRange[varPos])/(2*bin[varPos]);
  exh[m] = (endRange[varPos]-inRange[varPos])/(2*bin[varPos]);
  ratioUnityStatErr->SetBinContent(m+1,1);
  ratioUnityStatSysErr->SetBinContent(m+1,1);
  if(SumBkgs->GetBinContent(m+1)!=0) {
   ratioUnityStatErr->SetBinError(m+1,SumBkgs->GetBinError(m+1)/SumBkgs->GetBinContent(m+1));
   if(addsys){
    ratioUnityStatSysErr->SetBinError(m+1,SumBkgs_errStatSysBins[m]/SumBkgs->GetBinContent(m+1));
    SumBkgs->SetBinError(m+1,SumBkgs_errStatSysBins[m]); 
   }else{
    ratioUnityStatSysErr->SetBinError(m+1,SumBkgs->GetBinError(m+1)/SumBkgs->GetBinContent(m+1));
    SumBkgs->SetBinError(m+1,SumBkgs->GetBinError(m+1)); 
   }
   y[m]   = data->GetBinContent(m+1)/SumBkgs->GetBinContent(m+1);
   eyl[m] = sqrt(gData->GetErrorYlow(m)*gData->GetErrorYlow(m))/SumBkgs->GetBinContent(m+1);
   eyh[m] = sqrt(gData->GetErrorYhigh(m)*gData->GetErrorYhigh(m))/SumBkgs->GetBinContent(m+1);
  }else{
   y[m]   = -1;
   eyl[m] = 0;
   eyh[m] = 0;
  }
 }
 //ratioDataErr
 TGraphAsymmErrors* ratioDataErr = new TGraphAsymmErrors(bin[varPos],x,y,exl,exh,eyl,eyh);
 ratioDataErr->SetMarkerColor(1);
 ratioDataErr->SetMarkerStyle(20);
 ratioDataErr->SetMarkerSize(1.0);
 ratioDataErr->SetMaximum(1.7);
 ratioDataErr->SetMinimum(0.3);
 ratioDataErr->SetLineColor(1);
 ratioDataErr->SetLineWidth(2);
 ratioDataErr->GetXaxis()->SetTitleOffset(0.9);
 ratioDataErr->GetYaxis()->SetTitleOffset(0.5);
 ratioDataErr->SetTitle("");
 ratioDataErr->GetYaxis()->SetTitle("Data/Expectation");
 ratioDataErr->GetXaxis()->SetTitle(titleXaxis[varPos]);
 ratioDataErr->GetXaxis()->SetLabelSize(0.13);
 ratioDataErr->GetYaxis()->SetLabelSize(0.13);
 ratioDataErr->GetXaxis()->SetTitleSize(0.15);
 ratioDataErr->GetYaxis()->SetTitleSize(0.09);
 ratioDataErr->GetYaxis()->SetNdivisions(505);
 ratioDataErr->GetXaxis()->SetRangeUser(inRange[varPos],endRange[varPos]);
 return ratioDataErr;
}
THStack* get_hstack(TH1F* TTbar,TH1F* WJets,TH1F* dataDrivenDD,TH1F* Others){
 THStack* hs = new THStack("hs","hs");
 hs->Add(Others);
 hs->Add(dataDrivenDD);
 hs->Add(TTbar);
 hs->Add(WJets);
 hs->Draw("histo");
 hs->SetMinimum(0);
 hs->GetYaxis()->SetTitleSize(0.070);
 hs->GetXaxis()->SetTitleSize(0.070);
 hs->GetYaxis()->SetLabelSize(0.070);
 hs->GetXaxis()->SetLabelSize(0.0);
 hs->SetTitle("");
 hs->GetYaxis()->SetTitle("Events");
 hs->GetXaxis()->SetTitle("");
 hs->GetYaxis()->SetTitleOffset(0.80);
 hs->GetXaxis()->SetTitleOffset(0.85);
 return hs;
}
double get_maxy(TH1F* data, TH1F* SumBkgs){
 double maxy = -10;
 float ADD = 20;
 for(int ABC=0; ABC<data->GetNbinsX(); ABC++){
  if(SumBkgs->GetBinContent(ABC+1)+ADD>=maxy) maxy = SumBkgs->GetBinContent(ABC+1)+ADD;
  if(data->GetBinContent(ABC+1)+ADD>=maxy) maxy = data->GetBinContent(ABC+1)+ADD;
 }
 return maxy;
}
void get_marginsForLatex(float &t, float &b, float &r, float &l){
 TLatex latex;
 //Pad
 TPad *pad = new TPad("pad","pad",0.01,0.01,0.99,0.99);
 gPad->RedrawAxis();
 t = pad->GetTopMargin();
 b = pad->GetBottomMargin();
 r = pad->GetRightMargin();
 l = pad->GetLeftMargin();
}
////
//   Get parts of the plot (pad, legends, histo)
/////
TPad* get_pad(string name,string title,double xLow,double yLow,double xUp,double yUp,double topMargin,double bMargin,double rMargin,double lMargin){
 TPad *c = new TPad(name.c_str(),title.c_str(),xLow,yLow,xUp,yUp);
 c->SetTopMargin(topMargin);
 c->SetBottomMargin(bMargin);
 c->SetRightMargin(rMargin);
 c->SetLeftMargin(lMargin);
 return c;
} 
TH1F* get_th1f(string name,string var,int v){
 TH1F *th1f;
 if(var=="BJetness_num_vetonoipnoiso_leps" && doasym) th1f = new TH1F(name.c_str(),"",bin[v],asymbin);
 else                                                 th1f = new TH1F(name.c_str(),"",bin[v],inRange[v],endRange[v]);
 return th1f;
}
TLegend* get_legend(){
 TLegend *leg = new TLegend(0.53,0.56,0.95,0.91);
 //leg->SetHeader("");
 leg->SetBorderSize(0);
 leg->SetTextSize(0.04);
 leg->SetFillColor(0); 
 return leg;
}
