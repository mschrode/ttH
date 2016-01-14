#include <exception>
#include <iostream>
#include <map>
#include <vector>

#include "TCanvas.h"
#include "TFile.h"
#include "TH1.h"
#include "TH1D.h"
#include "TLegend.h"
#include "TPad.h"
#include "TString.h"
#include "TTree.h"

#include "Tools/Plotting/ErrorBand.h"
#include "Tools/Plotting/LabelMaker.h"
#include "Tools/Plotting/TheLooks.h"


TString niceLabel(const TString& category) {
  if( category == "ljets" )           return "combined";
  if( category == "ljets_j4_t3" )     return "4j3t";
  if( category == "ljets_j4_t4" )     return "4j4t";
  if( category == "ljets_j5_t3" )     return "5j3t";
  if( category == "ljets_j5_tge4" )   return "5j4t";
  if( category == "ljets_jge6_t2" )   return "6j2t";
  if( category == "ljets_jge6_t3" )   return "6j3t";
  if( category == "ljets_jge6_tge4" ) return "6j4t";
  return category;
}


TH1* getDistributionOfLimits(const TString& fileName, const TString& label, const TString& category) {
  std::cout << "Reading limits for '" << label << "' in category " << category << std::endl;

  // prepare histogram
  TH1* h = new TH1D(label+"_"+category,";limit("+niceLabel(category)+");N(experiments)",200,0,50);

  // read observed limits and fill distributions
  TFile file(fileName,"READ");
  TTree* tree = 0;
  file.GetObject("limit",tree);
  if( tree == 0 ) {
    std::cerr << "\nERROR reading " << category << " limit from file '" << fileName << "'\n" << std::endl;
    throw std::exception();
  }
  double limit = 0;
  float quantileExp = 0;
  tree->SetBranchAddress("limit",&limit);
  tree->SetBranchAddress("quantileExpected",&quantileExp);
  for(int i = 0; i < tree->GetEntries(); ++i) {
    tree->GetEntry(i);
    if( quantileExp < 0 ) h->Fill(limit);
  }
  delete tree;
  file.Close();

  return h;
}


std::map<TString,TH1*> getDistributionsOfLimits(const TString& fileNameBase, const TString& label, const std::vector<TString>& categories) {
  std::map<TString,TH1*> results;
  for(std::vector<TString>::const_iterator ic = categories.begin();
      ic != categories.end(); ++ic) {
    const TString fileName = fileNameBase+"_"+(*ic)+".root";
    results[*ic] = getDistributionOfLimits(fileName,label,*ic);
  }

  return results;
}


void plotDistributionsOfLimits(std::map<TString,TH1*>& dists, const TString& label) {
  TCanvas* can = new TCanvas("can","limits",500,500);
  for(std::map<TString,TH1*>::iterator it = dists.begin();
      it != dists.end(); ++it) {
    can->cd();
    it->second->SetLineColor(kBlack);
    it->second->SetLineWidth(2);
    it->second->Draw("HIST");
    can->SaveAs("Limits_"+label+"_"+niceLabel(it->first)+".pdf");
  }
  delete can;
}


void compareLimits(std::vector<TString>& categories, std::map<TString,TH1*>& dists1, const TString& label1, std::map<TString,TH1*>& dists2, const TString& label2) {

  TH1* hLimits1 = new TH1D("Limits_"+label1,";category;limit",categories.size(),0,categories.size());
  hLimits1->SetLineWidth(2);
  hLimits1->SetLineColor(kBlack);
  hLimits1->SetMarkerStyle(22);
  hLimits1->SetMarkerColor(hLimits1->GetLineColor());
  hLimits1->GetYaxis()->SetRangeUser(0,20);
  TH1* hLimits2 = static_cast<TH1*>(hLimits1->Clone("Limits_"+label2));
  hLimits2->SetLineColor(kRed);
  hLimits2->SetMarkerStyle(23);
  hLimits2->SetMarkerColor(hLimits2->GetLineColor());  

  int bin = 1;
  for(std::vector<TString>::iterator ic = categories.begin();
      ic != categories.end(); ++ic, ++bin) {
    std::map<TString,TH1*>::iterator id1 = dists1.find(*ic);
    if( id1 == dists1.end() ) {
      std::cerr << "\nERROR category '" << *ic << "' not found for '" << label1 << "'\n" << std::endl;
      throw std::exception();
    }
    std::map<TString,TH1*>::iterator id2 = dists2.find(*ic);
    if( id2 == dists2.end() ) {
      std::cerr << "\nERROR category '" << *ic << "' not found for '" << label2 << "'\n" << std::endl;
      throw std::exception();
    }

    hLimits1->GetXaxis()->SetBinLabel(bin,niceLabel(*ic));
    hLimits2->GetXaxis()->SetBinLabel(bin,niceLabel(*ic));

    hLimits1->SetBinContent(bin,id1->second->GetMean());
    hLimits1->SetBinError(bin,id1->second->GetRMS());
    hLimits2->SetBinContent(bin,id2->second->GetMean());
    hLimits2->SetBinError(bin,id2->second->GetRMS());
  }

  TH1* hLimitsRatio = static_cast<TH1*>(hLimits2->Clone("Ratio"));
  hLimitsRatio->Divide(hLimits1);
  hLimitsRatio->GetYaxis()->SetRangeUser(0,2);
  hLimitsRatio->GetYaxis()->SetTitle("limit("+label2+") / limit("+label1+")");

  TH1* hLimitsRatioFrame = static_cast<TH1*>(hLimitsRatio->Clone("RatioFrame"));
  for(int bin = 1; bin <= hLimitsRatioFrame->GetNbinsX(); ++bin) {
    hLimitsRatioFrame->SetBinContent(bin,1);
    hLimitsRatioFrame->SetBinError(bin,0);
  }
  hLimitsRatioFrame->SetLineWidth(2);
  hLimitsRatioFrame->SetLineStyle(2);
  hLimitsRatioFrame->SetLineColor(hLimits1->GetLineColor());

  TLegend* leg = LabelMaker::legendTR(2,0.4);
  leg->AddEntry(hLimits1,label1,"P");
  leg->AddEntry(hLimits2,label2,"P");

  TCanvas* can = new TCanvas("can","limits",500,500);
  can->cd();
  hLimits1->Draw("PE1");
  hLimits2->Draw("PE1same");
  leg->Draw("same");
  gPad->RedrawAxis();
  can->SaveAs("Limits_"+label2+"_vs_"+label1+".pdf");
  
  can->cd();
  hLimitsRatioFrame->Draw("HIST");
  hLimitsRatio->Draw("PE1same");
  gPad->RedrawAxis();
  can->SaveAs("Limits_"+label2+"_over_"+label1+".pdf");

  delete hLimits1;
  delete hLimits2;
  delete leg;
  delete can;
}


void plot_njetimpact() {
  const TString fileNameBase1  = "comb_limit_consistent";
  const TString label1 = "consistent";
  const TString fileNameBase2  = "comb_limit_inconsistent";
  const TString label2 = "inconsistent";

  TheLooks::set();
  
  std::vector<TString> categories;
  categories.push_back("ljets");
  categories.push_back("ljets_j4_t3");
  categories.push_back("ljets_j4_t4");
  categories.push_back("ljets_j5_t3");
  categories.push_back("ljets_j5_tge4");
  categories.push_back("ljets_jge6_t2");
  categories.push_back("ljets_jge6_t3");
  categories.push_back("ljets_jge6_tge4");

  std::map<TString,TH1*> limits1 = getDistributionsOfLimits(fileNameBase1,label1,categories);
  plotDistributionsOfLimits(limits1,label1);
  std::map<TString,TH1*> limits2 = getDistributionsOfLimits(fileNameBase2,label2,categories);
  plotDistributionsOfLimits(limits2,label2);
  compareLimits(categories,limits1,label1,limits2,label2);

  for(std::map<TString,TH1*>::iterator it = limits1.begin();
      it != limits1.end(); ++it) {
    delete it->second;
  }
}
