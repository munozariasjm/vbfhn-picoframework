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
//root files
const string pathFolder = "/afs/cern.ch/user/f/fromeo/public/4Brandon/"; 
const string task = "trial/";
const string year = "2018/";
int numSigs = 0; //Signals have to enter the first in *samples
int numBkgs = 1;
const char *samples[] = {"TTTo2L2Nu"}; 
const double lumiWeights[100] = {1};
double SF_Bkg1 = 1; 
const bool nodata = true;  
const string path = pathFolder+task+year+"mergedFiles/";
//tree and systematics
const bool addsys = false;
const int wsen = 1;
const string weights_sys[wsen] = {"main"};
const int ten = 1;
const string trees[ten] = {"Events"};
//variables
const unsigned int ini_var = 0;
const unsigned int fin_var = 1; 
const int    numVar = 1;
const char *variables[]         = {
"tau_pt"
};
const char *titleXaxis[]        = {
"tau_pt"
};
const int    bin[numVar]        = {
100
};
const double inRange[numVar]    = {
0
};
const double endRange[numVar]   = {
1000
};
//Plots
const bool save_plots   = false;
const bool show_title   = true;
const bool logYscale    = false;
/////
//   Declare functions 
/////
void get_th1f_variations(TH1F* Bkg1,string variable,int varPos);
void get_evt(TTree* tree,string variable,TH1F *hist);
TFile* Call_TFile(string rootpla);
TH1F* get_th1f(string name,string var,int v);
/////
//   Main function
/////
void stackPlots(){
 //Loop over all variables
 vector<string> vars(variables, variables + sizeof(variables)/sizeof(variables[0]));
 for(uint vr=ini_var; vr<fin_var; vr++){
  cout<<vars[vr]<<endl;
  TH1F* Bkg1 = get_th1f("Bkg1",vars[vr],vr); Bkg1->SetLineColor(kGreen+3); Bkg1->SetFillColor(kGreen+3);
  get_th1f_variations(Bkg1,vars[vr],vr);
  Bkg1->Draw();
 }
}
/////
//   Get the TH1F of all the contributions in the SignalRegion and the systematic errors
/////
void get_th1f_variations(TH1F* Bkg1,string variable,int varPos){
 //Loop over all samples
 vector<string> rootplas(samples, samples + sizeof(samples)/sizeof(samples[0]));
 int samplesSize = int(sizeof(samples)/sizeof(samples[0]));
 for(int r=0; r<samplesSize; r++){
  cout<<rootplas[r]<<endl;
  TFile* f = Call_TFile(rootplas[r]);
  TTree* tree; f->GetObject("Events",tree);
  get_evt(tree,variable,Bkg1);
  delete f;
 }//For samples
}
void get_evt(TTree* tree,string variable,TH1F *hist){
 double var; TBranch *b_var = 0; tree->SetBranchAddress(variable.c_str(),&var,&b_var); 
 for(int e=0; e<tree->GetEntries(); e++){
  Long64_t tentry = tree->LoadTree(e); 
  //The variable
  b_var->GetEntry(tentry);
  hist->Fill(var);
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
////
//   Get parts of the plot (pad, legends, histo)
/////
TH1F* get_th1f(string name,string var,int v){
 TH1F *th1f;
 th1f = new TH1F(name.c_str(),"",bin[v],inRange[v],endRange[v]);
 return th1f;
}
