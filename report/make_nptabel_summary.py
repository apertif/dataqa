#!/usr/bin/env python

import glob
import os
import numpy as np
import logging
import csv
import socket

# ----------------------------------------------
# read data from np file

logger = logging.getLogger(__name__)


def find_sources(obs_id, data_dir):
    """
    Identify preflag sources e.g. target name and calibrators
    """

    sources = []
    logs = glob.glob(data_dir+'/'+str(obs_id)+'/param_01_preflag_*.npy')

    for i in range(len(logs)):
        sources.append(logs[i][41:-4])

    return sources


def simplify_data(d, beamnum):
    """
    select relevant beam value from a list in a dictionary
    """
    dict = {}

    for k in d.keys():
        if np.iterable(d[k]):
            if len(d[k]) == 40:
                dict.update({k: d[k][beamnum]})
            if len(d[k]) == 12:
                chunks = ''
                for i in range(12):
                    if d[k][i] == False:
                        chunks = chunks+'F,'
                    else:
                        chunks = chunks+'T,'
                dict.update({k: chunks})
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

    Returns:
        a dictionary with information extracted from a numpy log file
    """

    #logger.info('Checking NPY files for beam {}'.format(beamnum))

    continuum_filters = ['targetbeams_mf_status', 'targetbeams_chunk_status']
    selfcal_filters = ['targetbeams_average', 'targetbeams_flagline',
                       'targetbeams_parametric', 'targetbeams_phase_status', 'targetbeams_amp_status']

    if module == 'selfcal' or module == 'continuum' or module == 'transfer':
        f = glob.glob(os.path.join(path, 'param_{:02d}.npy'.format(beamnum)))
    elif module == "crosscal":
        f = glob.glob(os.path.join(
            path, 'param_{:02d}_crosscal.npy'.format(beamnum)))
    else:
        f = glob.glob(os.path.join(
            path, 'param_{:02d}*{}*{}.npy'.format(beamnum, module, source)))

    res = {}
    dict_cut = {}

    # print(f)

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

            if module == 'continuum':
                for j in range(len(continuum_filters)):
                    if continuum_filters[j] in k:
                        res.update({continuum_filters[j]: d[k]})

            if module == 'selfcal':
                for j in range(len(selfcal_filters)):
                    if selfcal_filters[j] in k:
                        res.update({selfcal_filters[j]: d[k]})

            if module == 'transfer' and "transfer" in k:
                res.update({'transfer': d[k]})

        dict_cut = simplify_data(res, beamnum)

    else:
        #print('No file for beam: ', i)
        logger.info("No file for beam: {}".format(beamnum))

    logger.info("Extracting data for beam {} ... Done".format(beamnum))

    dict_cut.update({'beam': beamnum})

    return dict_cut


def extract_all_beams(obs_id, module, qa_dir):
    """
    Combine data from all beams into a directory.

    Args:
        obs_id (str): Directory of the data
        module (str): name of the apercal module e.g. 'preflag', 'convert', 'croscal'

    Returns
        a dictionary with information extracted from a numpy log file
    """
    if "data" in qa_dir:
        # beams_1 = '/data/apertif/'+str(obs_id)+'/'
        # beams_2 = '/data2/apertif/'+str(obs_id)+'/'
        # beams_3 = '/data3/apertif/'+str(obs_id)+'/'
        # beams_4 = '/data4/apertif/'+str(obs_id)+'/'

        # if not on happili, asssume all beamse
        # are on the same node. Not the best solution
        # for this, but requires the least amount of
        # changes to the logic below
        if socket.gethostname == "happili-01":
            # this gives /data/apertif/<taskid>
            beams_1 = os.path.dirname(qa_dir) + "/"
            beams_2 = os.path.dirname(qa_dir).replace("/data", "/data2") + "/"
            beams_3 = os.path.dirname(qa_dir).replace("/data", "/data3") + "/"
            beams_4 = os.path.dirname(qa_dir).replace("/data", "/data4") + "/"
        else:
            beams_1 = os.path.dirname(qa_dir) + "/"
            beams_2 = os.path.dirname(qa_dir) + "/"
            beams_3 = os.path.dirname(qa_dir) + "/"
            beams_4 = os.path.dirname(qa_dir) + "/"

    else:
        if socket.gethostname == "happili-01":
            beams_1 = os.path.dirname(qa_dir) + "/"
            beams_2 = os.path.dirname(qa_dir).replace("/tank", "/tank2") + "/"
            beams_3 = os.path.dirname(qa_dir).replace("/tank", "/tank3") + "/"
            beams_4 = os.path.dirname(qa_dir).replace("/tank", "/tank4") + "/"
        else:
            beams_1 = os.path.dirname(qa_dir) + "/"
            beams_2 = os.path.dirname(qa_dir) + "/"
            beams_3 = os.path.dirname(qa_dir) + "/"
            beams_4 = os.path.dirname(qa_dir) + "/"

    beamnum = np.arange(40)

    dict_beams = []

    if module == 'preflag':
        source_list = find_sources(obs_id, os.path.dirname(qa_dir))
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
            if i < 10:
                dict_beams.append(extract_beam(beams_1, i, module, source))

            if i >= 10 and i < 20:
                dict_beams.append(extract_beam(beams_2, i, module, source))

            if i >= 20 and i < 30:
                dict_beams.append(extract_beam(beams_3, i, module, source))

            if i >= 30 and i < 40:
                dict_beams.append(extract_beam(beams_4, i, module, source))

    return dict_beams


def make_nptabel_csv(obs_id, module, qa_dir, output_path=''):
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
    summary_data = extract_all_beams(obs_id, module, qa_dir)
    logger.info(
        "Reading param information for {0} of {1}... Done".format(module, obs_id))

    i = 0
    if module == 'transfer':
        while len(summary_data[i]) <= 1:
            i += 1
            if len(summary_data[i]) > 1:
                break
    else:
        while len(summary_data[i]) <= 2:
            i += 1
            if len(summary_data[i]) > 2:
                break

    csv_columns = summary_data[i].keys()

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
