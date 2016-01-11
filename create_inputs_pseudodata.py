# create set of inputs with pseudo data observed distributions
# (from Poisson around MC background)

import os
import ROOT
import sys

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)



in_file_name = sys.argv[1]
if not os.path.isfile(in_file_name):
    print "\nERROR not a regular file '"+in_file_name+"'\n"
    sys.exit()
if not in_file_name.endswith("inputs_base.root"):
    print "\nERROR input file seems not to be correct (does not end with 'inputs_base.root')\n"
    sys.exit()

n_samples = 1000
if len(sys.argv) > 2:
    n_samples = int(sys.argv[2])

processes =['ttbarOther','ttbarPlusCCbar','ttbarPlusB','ttbarPlus2B','ttbarPlusBBbar' ]
categories = ["j4_t3",
              "j4_t4",
              "j5_t3",
              "j5_tge4",
              "jge6_t2",
              "jge6_t3",
              "jge6_tge4"]

print "Creating "+str(n_samples)+" pseudo experiments:"

plots_dir = os.path.dirname(in_file_name)
print "Working dir: '"+plots_dir+"'"
file_name_base = os.path.basename(in_file_name)  # should read '<some file name>_inputs_base.root'
print "Base file name: '"+file_name_base+"'"

rand = ROOT.TRandom3(0)
for iExp in xrange(n_samples):
    out_dir = plots_dir+"/"+file_name_base.replace("base.root","pseudodata_"+str(iExp))
    os.system("mkdir -p "+out_dir)
    out_file_name = file_name_base.replace("base.root","pseudodata_"+str(iExp)+".root")
    print "Creating file '"+out_file_name+"'"
    os.system("cp "+in_file_name+" "+out_dir+"/"+out_file_name) # will overwrite existing file

    with cd(out_dir):
        out_file = ROOT.TFile(out_file_name,"UPDATE")
        for icat in categories:
            # clone hist for the first process, will be the data_obs_<discr>_<categ> distribution
            process = processes[0]
            name = process+"_BDT_ljets_"+icat
            hist = out_file.Get(name)
#            print "Cloning "+hist.GetName()
            name = name.replace(process,"data_obs")
            hist_data = hist.Clone(name)
            hist_data.SetTitle(name)
#            print "  --> "+hist_data.GetName()
#            print "  Int = "+str(hist_data.Integral())
            # now, add the hists for the other processes
            for iproc in processes[1:]:  
                hist = out_file.Get(iproc+"_BDT_ljets_"+icat)
#                print "    Adding "+hist.GetName()
                hist_data.Add(hist)
#                print "    Int = "+str(hist_data.Integral())
            # set new bin content, Poisson smeared around the original content
            # (sum of processes)
            for ibin in xrange(1,hist_data.GetNbinsX()+1):
                mean = hist_data.GetBinContent(ibin)
                hist_data.SetBinContent(ibin,rand.Poisson(mean))
                hist_data.SetBinError(ibin,0)
#                print "  Smear bin ("+str(ibin)+") content "+str(mean)+" --> "+str(hist_data.GetBinContent(ibin))
            # write data_obs to file
            hist_data.Write()
        
        out_file.Close()
