#!/usr/bin/env python2

"""Input a continuum image and produce a validation report (in html) in a directory named after the image, which summarises
several validation tests/metrics (e.g. astrometry, flux scale, source counts, etc) and whether the data passed or failed these tests.

Modification of the original code by Jordan Collier (https://github.com/Jordatious/ASKAP-continuum-validation)

Usage:
  validation.py -h | --help
  validation.py [-S --Selavy=<cat>] [-z --bdsm] [-P --PyBDSFcat=<cat>] [-N --noise=<map>] [-C --catalogues=<list>]
  [-F --filter=<config>] [-R --snr=<ratio>] [-v --verbose] [-f --refind] [-r --redo] [-p --peak-flux]
  [-w --write] [-x --no-write] [-m --SEDs=<models>] [-e --SEDfig=<extn>] [-d --main-dir=<path>]
  [-n --ncores=<num>] [-b --nbins=<num>] [-s --source=<src>] [-a --aegean-params] <fits-file>

Arguments:
  <fits-file>               A fits continuum image.

Options:
  -h --help                 Show this help message.
  -S --Selavy=<cat>         Use this Selavy catalogue of the input image. Default is to run Aegean [default: None].
  -z --bdsm                 Run PyBDSM [default: False]
  -P --PyBDSFcat=<cat>          Use this Pybdsf catalogue of the input image. Default is to run Aegean [default: None].
  -N --noise=<map>          Use this fits image of the local rms. Default is to run BANE [default: None].
  -C --catalogues=<list>    A comma-separated list of filepaths to catalogue config files corresponding to catalogues to use
                            (will look in --main-dir for each file not found in given path) [default: FIRST_config.txt, NVSS_config.txt, TGSS_config.txt].
  -F --filter=<config>      A config file for filtering the sources in the catalogue [default: None].
  -R --snr=<ratio>          The signal-to-noise ratio cut to apply to the catalogue and the source counts (doesn't affect source finding) [default: 5.0].
  -v --verbose              Verbose output [default: False].
  -f --refind               Force source finding step, even when catalogue already exists (sets --redo to True) [default: False].
  -r --redo                 Force every step again (except source finding), even when catalogues already exist [default: False].
  -p --peak-flux            Use the peak flux rather than the integrated flux of the catalogue [default: False].
  -w --write                Write intermediate files generated during processing (e.g. cross-matched and pre-filtered catalogues, etc).
                            This will save having to reprocess the cross-matches, etc when executing the script again. [default: False].
  -x --no-write             Don't write any files except the html report (without figures) and any files output from BANE and Aegean. [default: False].
  -m --SEDs=<models>        A comma-separated list of SED models to fit to the radio spectra ('pow','SSA','FFA','curve',etc) [default: None].
  -e --SEDfig=<extn>        Write figures for each SED model with this file extension (will significantly slow down script) [default: None].
  -d --main-dir=<path>      The absolute path to the main directory where this script and other required files are located [default: None].
  -n --ncores=<num>         The number of cores (per node) to use when running BANE and Aegean (using >=20 cores may result in memory error) [default: 8].
  -b --nbins=<num>          The number of bins to use when performing source counts [default: 50].
  -s --source=<src>         The format for writing plots (e.g. screen, html, eps, pdf, png, etc) [default: html].
  -a --aegean=<params>      A single string with extra paramters to pass into Aegean (except cores, noise, background, and table) [default: --floodclip=3]."""

from __future__ import division
from docopt import docopt
import os
import sys
# from datetime import datetime
import warnings
from inspect import currentframe, getframeinfo

#Set my own obvious warning output
cf = currentframe()
WARN = '\n\033[91mWARNING: \033[0m' + getframeinfo(cf).filename

#Raise error if user tries to pass in noise map and then run Aegean
try:
    args = docopt(__doc__)
    if args['--Selavy'] == 'None' and args['--noise'] != 'None':
        raise SyntaxError
except SyntaxError:
    warnings.warn_explicit("""When no Selavy catalogue is passed in (option -S), you cannot input a noise map (option -N).\n""",UserWarning,WARN,cf.f_lineno)
    sys.exit()

#don't use normal display environment unless user wants to view plots on screen
import matplotlib as mpl
if args['--source'] != 'screen':
    mpl.use('Agg')

from functions import find_file, parse_string, new_path, changeDir, config2dic
from radio_image import radio_image
from catalogue import catalogue
from report import report

#find directory that contains all the necessary files
main_dir = args['--main-dir']

if main_dir == 'None':
    main_dir, _ = os.path.split(os.path.realpath(__file__))



#Set paramaters passed in by user
img = find_file(parse_string(args['<fits-file>']),main_dir)
verbose = args['--verbose']
source = args['--source']
refind = args['--refind']
redo = args['--redo'] or refind #force redo when refind is True
use_peak = args['--peak-flux']
write_any = not args['--no-write']
write_all = args['--write']
aegean_params = args['--aegean']
ncores = int(args['--ncores'])
nbins = int(args['--nbins'])
snr = float(args['--snr'])
config_files = args['--catalogues'].split(',')
SEDs = args['--SEDs'].split(',')
SEDextn = parse_string(args['--SEDfig'])
do_PyBDSF = args['--bdsm']

if args['--SEDs'] == 'None':
    SEDs = 'pow'
    fit_flux=False
else:
    fit_flux=True

#force write_all=False write_any=False
if not write_any:
    write_all = False

#add '../' to relative paths of these files, since
#we'll create and move into a directory for output files
filter_config = new_path(parse_string(args['--filter']))
selavy_cat = new_path(parse_string(args['--Selavy']))
pybdsf_cat = new_path(parse_string(args['--PyBDSFcat']))
noise = new_path(parse_string(args['--noise']))

if __name__ == "__main__":

    #Run Aegean / PyBDSF for source finding or use input Selavy catalogue
    if selavy_cat is not None:
        main_cat = selavy_cat
        finder = 'selavy'
    elif pybdsf_cat is not None or do_PyBDSF:
        main_cat = pybdsf_cat
        finder = 'pybdsf'
    else:
        finder = 'aegean'

    #add S/N and peak/int to output directory/file names
    suffix = '{0}_snr{1}_'.format(finder, snr)
    if use_peak:
        suffix += 'peak'
    else:
        suffix += 'int'

    #Load image
    changeDir(img,suffix, verbose=verbose)
    img = new_path(img)
    IMG = radio_image(img, verbose=verbose, finder=finder, rms_map=noise, SNR=snr)

    #Run BANE if user hasn't input noise map
    if noise is None:
        IMG.run_BANE(ncores=ncores, redo=refind)


    #Run Aegean if user didn't pass in Selavy catalogue
    if finder == 'aegean':
        main_cat = IMG.cat_comp
        IMG.run_Aegean(ncores=ncores, redo=refind, params=aegean_params, write=write_any)
    elif finder == 'pybdsf':
        main_cat = IMG.cat_comp
        IMG.run_PyBDSF(ncores=ncores, redo=refind, params=aegean_params, write=write_any)


    #Create catalogue object
    CAT = catalogue(main_cat, 'APERTIF', finder=finder, image=IMG, SNR=snr,
                    verbose=verbose, autoload=False, use_peak=use_peak)

    #Filter out sources below input SNR, set specs and create report object before filtering
    #catalogue further so specs and source counts can be written for all sources above input SNR
    CAT.filter_sources(SNR=snr, flags=True, redo=redo, write=write_any,
                       verbose=verbose, file_suffix='_snr{0}'.format(snr))
    CAT.set_specs(IMG)
    REPORT = report(CAT, main_dir, img=IMG, verbose=verbose, plot_to=source, redo=redo,
                    src_cnt_bins=nbins, write=write_any)

    #use config file for filtering sources if it exists
    if filter_config is not None:
        if verbose:
            print "Using config file '{0}' for filtering.".format(filter_config)
        filter_dic = config2dic(filter_config,main_dir,verbose=verbose)
        filter_dic.update({'redo' : redo, 'write' : write_all, 'verbose' : verbose})
        CAT.filter_sources(**filter_dic)
    else:
        #otherwise use default criteria, selecting reliable point sources for comparison
        CAT.filter_sources(flux_lim=1e-5, ratio_frac=0, ratio_sigma=0,
                           reject_blends=False,
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
                                write_all=write_all, write_any=write_any)

    #Fit radio SED models using all fluxes except
    #, and derive the flux at frequency
    if len(CAT.cat_list) > 1:
        CAT.fit_spectra(redo=redo, models=SEDs, GLEAM_subbands='int',
                        GLEAM_nchans=4, cat_name=None, write=write_any,
                        fit_flux=fit_flux, fig_extn=SEDextn)

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
