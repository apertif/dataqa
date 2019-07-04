#!/usr/bin/env python

import glob
import os
import numpy as np
import logging
import csv

# ----------------------------------------------
# read data from np file

logger = logging.getLogger(__name__)


def find_sources(obs_id):
    """
    Identify preflag sources e.g. target name and calibrators
    """

    sources = []
    logs = glob.glob('/data/apertif/'+str(obs_id)+'/param_01_preflag_*.npy')

    for i in range(len(logs)):
        sources.append(logs[i][41:-4])

    return sources


def simplify_data(d, beamnum):
    """
    select relevant beam value from a list in a dictionary
    """
    dict = {}

    for k in d.keys():
        if np.iterable(d[k]) and len(d[k]) == 40:
            dict.update({k: d[k][beamnum]})
        else:
            dict.update({k: d[k]})

    return dict


def extract_beam(path, beamnum, module, source):
    """
    Function to return numpy files contents as a dictionary filtered for certain keys

    Args:
                    path (str): Directory of the data
                    beamnum (int): Beam number
                    module (str): name of the apercal module e.g. 'preflag', 'convert', 'croscal'
                    source (str): name of the source or calibrators for preflag, for other modules it should be an empty string ('')

    Returns
                    a dictionary with information extracted from a numpy log file
    """

    # logger.info('Checking NPY files for beam {}'.format(beamnum))

    f = glob.glob(os.path.join(
        path, 'param_{:02d}*{}*{}.npy'.format(beamnum, module, source)))
    res = {}
    dict_cut = {}

    if len(f) != 0:
        d = np.load(f[0]).item()

        for k in d.keys():
            if module == 'preflag' and "targetbeams" in k:
                res.update({k: d[k]})

            if module == 'crosscal':
                res.update({k: d[k]})

            if module == 'convert' and "UVFITS2MIRIAD" in k:
                res.update({k: d[k]})

            if module == 'convert' and "MS2UVFITS" in k:
                res.update({k: d[k]})

        dict_cut = simplify_data(res, beamnum)

    else:
        # print('No file for beam: ', i)
        logger.info("No file for beam: {}".format(beamnum))

    logger.info("Extracting data ... Done")

    dict_cut.update({'beam': beamnum})

    return dict_cut


def extract_all_beams(obs_id, module):
    """
    Combine data from all beams into a directory.

    Args:
        obs_id (str): Directory of the data
        module (str): name of the apercal module e.g. 'preflag', 'convert', 'croscal'

    Returns
        a dictionary with information extracted from a numpy log file
    """

    beams_1 = '/data/apertif/'+str(obs_id)+'/'
    beams_2 = '/data2/apertif/'+str(obs_id)+'/'
    beams_3 = '/data3/apertif/'+str(obs_id)+'/'
    beams_4 = '/data4/apertif/'+str(obs_id)+'/'

    beamnum = np.arange(40)

    dict_beams = []

    if module == 'preflag':
        source_list = find_sources(obs_id)
        for j in range(len(source_list)):
            for i in beamnum:
                if i < 10:
                    dict_beams_v1 = (extract_beam(
                        beams_1, i, module, source_list[j]))
                    dict_beams_v1.update({'source': source_list[j]})
                    dict_beams.append(dict_beams_v1)

                if i >= 10 and i < 20:
                    dict_beams_v1 = (extract_beam(
                        beams_2, i, module, source_list[j]))
                    dict_beams_v1.update({'source': source_list[j]})
                    dict_beams.append(dict_beams_v1)

                if i >= 20 and i < 30:
                    dict_beams_v1 = (extract_beam(
                        beams_3, i, module, source_list[j]))
                    dict_beams_v1.update({'source': source_list[j]})
                    dict_beams.append(dict_beams_v1)

                if i >= 30 and i < 40:
                    dict_beams_v1 = (extract_beam(
                        beams_4, i, module, source_list[j]))
                    dict_beams_v1.update({'source': source_list[j]})
                    dict_beams.append(dict_beams_v1)

    else:
        source = ''

        for i in beamnum:
            if i < 11:
                dict_beams.append(extract_beam(beams_1, i, module, source))

            if i > 10 and i < 21:
                dict_beams.append(extract_beam(beams_2, i, module, source))

            if i > 20 and i < 31:
                dict_beams.append(extract_beam(beams_3, i, module, source))

            if i > 30 and i < 40:
                dict_beams.append(extract_beam(beams_4, i, module, source))

    return dict_beams


def make_nptabel_csv(obs_id, module, output_path=''):
    """
    Creates a dictionary with the summary into
    from the numpy files and saves it as a csv file.

    Args:
            obs_id (str): ID of observation
            module (str): Apercal module for which information are extracted
            output_path (str): Optional path to where the information is save (default current directory)

    """

    logger.info(
        "Reading param information for {0} of {1}".format(module, obs_id))
    summary_data = extract_all_beams(obs_id, module)
    logger.info(
        "Reading param information for {0} of {1}... Done".format(module, obs_id))

    i = 0
    while len(summary_data[i]) <= 2:
        i += 1
        if len(summary_data[i]) > 2:
            break

    csv_columns = summary_data[i].keys()
    # print csv_columns

    csv_columns.sort()
    dict_data = summary_data

    # save the file
    if output_path == '':
        csv_file = str(obs_id)+"_"+str(module)+"_summary.csv"
    else:
        csv_file = os.path.join(output_path, str(
            obs_id)+"_"+str(module)+"_summary.csv")
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
    except Exception as e:
        logger.warning("Creating file {} failed".format(csv_file))
        logger.exception(e)

    # print("Created file: "+str(obs_id)+"_"+str(module)+"_summary.csv")
    logger.info("Creating file: {} ... Done".format(csv_file))
