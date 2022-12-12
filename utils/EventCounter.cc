/**
This Macro
1. Calls the tree "evtree" and counts the mc events that have been read

Need to specify
0. See Declare constants
*/
/////
//   To run: root -l EventCounter.cc+'("rootplas","var")' 
/////
/////
//   Prepare Root and Roofit
/////
#include "TFile.h"
#include "TTree.h"
#include <iostream>
using namespace std;
////
//   Declare constants
/////
//Path - samples 
const string path     = "";
const string dotroot   = ".root"; 
/////
//   Declare functions 
/////
TFile* Call_TFile(string rootpla);
/////
//   Main function
/////
void EventCounter(string rootplas, string var){
 TFile* f = Call_TFile(rootplas); TTree* tree; f->GetObject("evtree",tree);
 double curr_var;
 TBranch *b_curr_var = 0;
 tree->SetBranchAddress(var.c_str(),&curr_var,&b_curr_var);
 int sum = 0;
 for(uint i=0; i<tree->GetEntries(); i++){
  Long64_t tentry = tree->LoadTree(i);
  b_curr_var->GetEntry(tentry);
  sum = sum+curr_var;
 }
 cout<<"Read evt are: "<<sum<<endl;
}
/////
//   Call TFile to be read
/////
TFile* Call_TFile(string rootpla){
 string file_name = path+rootpla+dotroot;
 TFile* f = new TFile(file_name.c_str(),"update");
 return f;
}
