#!/usr/bin/env python

# create set of inputs with pseudo data observed distributions
# (from Poisson around MC background)

import optparse
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


optParser = optparse.OptionParser()
optParser.add_option("-i", "--input", dest="in_file_name")
optParser.add_option("-n", "--numexp", dest="n_samples")
optParser.add_option("-d", "--data", dest="ext_file_name")
(pars,args) = optParser.parse_args(sys.argv[1:])

if pars.in_file_name is None:
    print "\nERROR: No input file with background templates specified\n"
    sys.exit()
if not os.path.isfile(pars.in_file_name):
    print "\nERROR not a regular file '"+pars.in_file_name+"'\n"
    sys.exit()
if not pars.in_file_name.endswith("inputs_base.root"):
    print "\nERROR input file seems not to be correct (does not end with 'inputs_base.root')\n"
    sys.exit()

if pars.n_samples is None:
    print "\nERROR number of pseudo experiments not specified\n"
    sys.exit()

if pars.ext_file_name is None:
    get_data_from_external = False
else:
    get_data_from_external = True
    if not os.path.isfile(pars.ext_file_name):
        print "\nERROR not a regular file '"+pars.ext_file_name+"'\n"
        sys.exit()
    if not ( pars.ext_file_name.endswith("_0.root") and pars.ext_file_name.contains("_0/") ):
        print "\nERROR wrong format of input file name for data histograms"
        print "Must be <some path>/<name>_0/<other name>_0.root \n"
        sys.exit()

processes =['ttbarOther','ttbarPlusCCbar','ttbarPlusB','ttbarPlus2B','ttbarPlusBBbar' ]
categories = ["j4_t3",
              "j4_t4",
              "j5_t3",
              "j5_tge4",
              "jge6_t2",
              "jge6_t3",
              "jge6_tge4"]


plots_dir = os.path.dirname(pars.in_file_name)
print "Working dir: '"+plots_dir+"'"
file_name_base = os.path.basename(pars.in_file_name)  # should read '<some file name>_inputs_base.root'
print "Base file name: '"+file_name_base+"'"

if get_data_from_external:
    print "Copying data histograms from '"+pars.ext_file_name.replace("_0","_NN")+"' ('_NN' = 0.."+str(pars.n_samples-1)+")"
else:
    print "Creating "+str(pars.n_samples)+" pseudo experiments:"
rand = ROOT.TRandom3(0)
for iExp in xrange(pars.n_samples):
    out_dir = plots_dir+"/"+file_name_base.replace("base.root","pseudodata_"+str(iExp))
    os.system("mkdir -p "+out_dir)
    out_file_name = file_name_base.replace("base.root","pseudodata_"+str(iExp)+".root")
    print "Creating file '"+out_file_name+"'"
    os.system("cp "+pars.in_file_name+" "+out_dir+"/"+out_file_name) # will overwrite existing file

    if get_data_from_external:
        # retrieve data histograms from external files and add to output
        with cd(out_dir):
            out_file = ROOT.TFile(out_file_name,"UPDATE")
            ext_file_name_iexp = pars.ext_file_name.replace("_0.root","_"+str(iExp)+".root").replace("_0/","_"+str(iExp)+"/")
            if not os.path.isfile(ext_file_name_iexp):
                print "\nERROR not a regular file '"+ext_file_name_iexp+"'\n"
                sys.exit()
            print "  Getting data histograms from '"+ext_file_name_iexp+"'"
            ext_file = ROOT.TFile(ext_file_name_iexp,"READ")
            for icat in categories:
                name = "data_obs_BDT_ljets_"+icat
                hist = ext_file.Get(name)
                out_file.WriteTObject(hist)
            ext_file.Close()
            out_file.Close()

    else:
        # create pseudo data from sum of backgrounds and add histograms to output file
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
