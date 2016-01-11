# extract the BDT distributions needed as inputs to combine

import sys
import ROOT

in_file_name = sys.argv[1]
out_file_name = in_file_name.replace(".root","_inputs_base.root")

processes =['ttH125','ttbarOther','ttbarPlusCCbar','ttbarPlusB','ttbarPlus2B','ttbarPlusBBbar' ]
categories = ["j4_t3",
              "j4_t4",
              "j5_t3",
              "j5_tge4",
              "jge6_t2",
              "jge6_t3",
              "jge6_tge4"]
variations = ["",
              "_CMS_ttH_CSVLFUp","_CMS_ttH_CSVLFDown","_CMS_ttH_CSVHFUp","_CMS_ttH_CSVHFDown",
              "_CMS_ttH_CSVHFStats1Up","_CMS_ttH_CSVHFStats1Down","_CMS_ttH_CSVLFStats1Up","_CMS_ttH_CSVLFStats1Down",
              "_CMS_ttH_CSVHFStats2Up","_CMS_ttH_CSVHFStats2Down","_CMS_ttH_CSVLFStats2Up","_CMS_ttH_CSVLFStats2Down",
              "_CMS_ttH_CSVCErr1Up","_CMS_ttH_CSVCErr1Down","_CMS_ttH_CSVCErr2Up","_CMS_ttH_CSVCErr2Down",
              "_CMS_scale_jUp","_CMS_scale_jDown"]#,"_CMS_res_jUp","_CMS_res_jDown"]

in_file = ROOT.TFile(in_file_name,"READ")
out_file = ROOT.TFile(out_file_name,"RECREATE")

for iproc in processes:
    for icat in categories:
        for ivar in variations:
            hist_name = iproc+"_BDT_ljets_"+icat+ivar
            print "Writing '"+hist_name+"'"
            hist = in_file.Get(hist_name)
            out_file.WriteTObject(hist)

out_file.Close()
in_file.Close()
