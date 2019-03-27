#!/usr/bin/env python2

from __future__ import division
import os
# from datetime import datetime
from inspect import currentframe, getframeinfo
#Set my own obvious warning output
cf = currentframe()
WARN = '\n\033[91mWARNING: \033[0m' + getframeinfo(cf).filename

from functions import find_file, config2dic, changeDir
from radio_image import radio_image
from catalogue import catalogue
from report import report

def run(fits_image, finder='pybdsf', snr=5.0, verbose=True, refind=False, redo=False,
        config_files=['FIRST_config.txt', 'NVSS_config.txt', 'TGSS_config.txt'],
        use_peak=False, ncores=8, nbins=50, filter_config=None, write_all=True,
        aegean_params='--floodclip=3', pybdsf_params=dict()):

    #find directory that contains all the necessary files
    main_dir, _ = os.path.split(os.path.realpath(__file__))

    #Set paramaters passed in by user
    img = os.path.abspath(fits_image)

    suffix = '{0}_snr{1}_'.format(finder, snr)
    if use_peak:
        suffix += 'peak'
    else:
        suffix += 'int'

    changeDir(img, suffix, verbose=verbose)

    #Load image
    IMG = radio_image(img, verbose=verbose, finder=finder, SNR=snr)

    #Run Aegean if user didn't pass in Selavy catalogue
    if finder == 'aegean':
        main_cat = IMG.cat_comp
        IMG.run_Aegean(ncores=ncores, redo=refind, params=aegean_params, write=write_all)
    elif finder == 'pybdsf':
        main_cat = IMG.cat_comp
        IMG.run_PyBDSF(ncores=ncores, redo=refind, pybdsf_params=pybdsf_params, write=write_all)


    #Create catalogue object
    CAT = catalogue(main_cat, 'APERTIF', finder=finder, image=IMG, SNR=snr,
                    verbose=verbose, autoload=False, use_peak=use_peak)

    #Filter out sources below input SNR, set specs and create report object before filtering
    #catalogue further so specs and source counts can be written for all sources above input SNR
    CAT.filter_sources(SNR=snr, flags=True, redo=redo, write=write_all,
                       verbose=verbose, file_suffix='_snr{0}'.format(snr))
    CAT.set_specs(IMG)
    REPORT = report(CAT, main_dir, img=IMG, verbose=verbose, plot_to='html', redo=redo,
                    src_cnt_bins=nbins, write=write_all)

    # use config file for filtering sources if it exists
    if filter_config is not None:
        if verbose:
            print "Using config file '{0}' for filtering.".format(filter_config)
        filter_dic = config2dic(filter_config,main_dir,verbose=verbose)
        filter_dic.update({'redo' : redo, 'write' : write_all, 'verbose' : verbose})
        CAT.filter_sources(**filter_dic)
    else:
    # otherwise use default criteria, selecting reliable point sources for comparison
        CAT.filter_sources(flux_lim=1e-3, ratio_frac=1.4, ratio_sigma=0,
                           reject_blends=True,
                           flags=False, psf_tol=1.5, resid_tol=3,
                           redo=redo, write=write_all, verbose=verbose)

    #process each catalogue object according to list of input catalogue config files
    #this will cut out a box, cross-match to this instance, and derive the spectral indices.
    for config_file in config_files:
        if verbose:
            print "Using config file '{0}' for catalogue.".format(config_file)
        config_file = config_file.strip() #in case user put a space
        config_file = find_file(config_file,main_dir, verbose=verbose)
        CAT.process_config_file(config_file, main_dir, redo=redo,
                                verbose=verbose,
                                write_all=write_all, write_any=write_all)

# Fit radio SED models using all fluxes except and derive the flux at frequency
    if len(CAT.cat_list) > 1:
        CAT.fit_spectra(redo=redo, models=None, GLEAM_subbands='int',
                        GLEAM_nchans=4, cat_name=None, write=write_all)

    print "----------------------------"
    print "| Running validation tests |"
    print "----------------------------"

    #Produce validation report for each cross-matched catalogue
    for cat_name in CAT.cat_list[1:]:
        REPORT.validate(CAT.name, cat_name, redo=redo)

    #write file with RA/DEC offsets for pipeline
    #and append validation metrics to html file and then close it
    REPORT.write_pipeline_offset_params()
    REPORT.write_html_end()

if __name__ == "__main__":
    print("Hello!")