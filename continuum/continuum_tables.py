# This module contains functionality to merge the image properties tables

import os
import glob
from astropy.table import Table, vstack
import numpy as np
import logging

logger = logging.getLogger(__name__)


def merge_continuum_image_properties_table(obs_id, qa_dir, single_node=False):
    """
    This function combines the image properties tables from the different 
    """

    # the original tables
    cont_table_file_1 = os.path.join(
        qa_dir, "continuum/continuum_image_properties.csv")
    if "/data" in qa_dir:
        cont_table_file_2 = os.path.join(
            qa_dir.replace("/data/", "/data2/"), "continuum/continuum_image_properties.csv")
        cont_table_file_3 = os.path.join(
            qa_dir.replace("/data/", "/data3/"), "continuum/continuum_image_properties.csv")
        cont_table_file_4 = os.path.join(
            qa_dir.replace("/data/", "/data4/"), "continuum/continuum_image_properties.csv")
    else:
        cont_table_file_2 = os.path.join(
            qa_dir.replace("/tank/", "/tank2/"), "continuum/continuum_image_properties.csv")
        cont_table_file_3 = os.path.join(
            qa_dir.replace("/tank/", "/tank3/"), "continuum/continuum_image_properties.csv")
        cont_table_file_4 = os.path.join(
            qa_dir.replace("/tank/", "/tank4/"), "continuum/continuum_image_properties.csv")

    # read the content and get only the relevant beams
    combined_table = []

    # check that table exists, then get content
    if os.path.exists(cont_table_file_1):
        cont_data_1 = Table.read(cont_table_file_1, format="ascii.csv")

        # if everything is on one node, the next line is not necessary
        if not single_node:
            cont_data_1_beams = cont_data_1[np.where(
                (cont_data_1['beam'] >= 0) & (cont_data_1['beam'] <= 9))]
            combined_table.append(cont_data_1_beams)
        else:
            combined_table.append(cont_data_1)
    else:
        logger.warning("Could not find {}".format(cont_table_file_1))

    # check that table exists, then get content
    if os.path.exists(cont_table_file_2):
        cont_data_2 = Table.read(cont_table_file_2, format="ascii.csv")
        cont_data_2_beams = cont_data_2[np.where(
            (cont_data_2['beam'] >= 10) & (cont_data_2['beam'] <= 19))]
        combined_table.append(cont_data_2_beams)
    else:
        logger.warning("Could not find {}".format(cont_table_file_2))

    # check that table exists, then get content
    if os.path.exists(cont_table_file_3):
        cont_data_3 = Table.read(cont_table_file_3, format="ascii.csv")
        cont_data_3_beams = cont_data_3[np.where(
            (cont_data_3['beam'] >= 20) & (cont_data_3['beam'] <= 29))]
        combined_table.append(cont_data_3_beams)
    else:
        logger.warning("Could not find {}".format(cont_table_file_3))

    # check that table exists, then get content
    if os.path.exists(cont_table_file_4):
        cont_data_4 = Table.read(cont_table_file_4, format="ascii.csv")
        cont_data_4_beams = cont_data_4[np.where(
            (cont_data_4['beam'] >= 30) & (cont_data_4['beam'] <= 39))]
        combined_table.append(cont_data_4_beams)
    else:
        logger.warning("Could not find {}".format(cont_table_file_4))

    # check the length of the new table to make sure it is not empty
    if len(combined_table) != 0:
        new_table = vstack(combined_table)
        new_table_name = os.path.join(
            qa_dir, "continuum/{}_combined_continuum_image_properties.csv".format(obs_id))
        new_table.write(new_table_name, format="ascii.csv", overwrite=True)
    else:
        logger.warning("No tables with continuum image properties found")
