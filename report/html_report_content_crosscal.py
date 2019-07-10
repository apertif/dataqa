import os
import sys
from astropy.table import Table
import logging
import glob
import time
import socket
import numpy as np

logger = logging.getLogger(__name__)


def write_obs_content_crosscal(html_code, qa_report_obs_path, page_type, obs_info=None):
    """Function to create the html page for crosscal

    Args:
        html_code (str): HTML code with header and title
        qa_report_obs_path (str): Path to the report directory
        page_type (str): The type of report page

    Return:
        html_code (str): Body of HTML code for this page
    """

    logger.info("Writing html code for page {0:s}".format(page_type))

    html_code += """
        <div class="w3-container w3-large">
            <p>
                This page provides information on the performance of the crosscal module. You can find the following information here: 
            </p>
            <div class="w3-container w3-large">
                1. Table of the crosscal quality parameters from the pipeline separated for target, flux calibrator and polarisation calibrator.<br>
                2. Various plots related to the cross calibration<br>
            </div>
        </div>\n
        """

    qa_report_obs_page_path = os.path.join(qa_report_obs_path, page_type)

    # Create html code for summary table
    # ==================================

    if obs_info is not None:
        obs_id = obs_info['Obs_ID'][0]
        source_list = np.array(
            [obs_info['Target'][0], obs_info['Flux_Calibrator'][0], obs_info['Pol_Calibrator'][0]])
    else:
        obs_id = os.path.basename(qa_report_obs_path)
        source_list = None

    # set the file name
    crosscal_summary_file = os.path.join(
        qa_report_obs_page_path, "{0}_{1}_summary.csv".format(obs_id, page_type))

    if os.path.exists(crosscal_summary_file):
        summary_table = Table.read(crosscal_summary_file, format="ascii.csv")

    else:
        summary_table = None

    # if there is a summary table
    # create tables for each source
    if summary_table is not None:

        # get the keys for the table
        table_keys = summary_table.keys()

        html_code += """
            <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('gallery-1')">
                        Crosscal summary table
                    </button>
                </div>
            <div class="w3-container w3-margin-top w3-hide" name="gallery-1">\n"""

        beam_list = summary_table['beam']

        # go through the list of sources
        for pos, source in enumerate(source_list):
            if source != '':
                # if it is the first source, get the target information
                if pos == 0:
                    keyword = "target"
                # if is the second, get the flux calibrator
                elif pos == 1:
                    keyword = "fluxcal"
                # otherwise it is the pol calibrator
                else:
                    keyword = "polcal"

                div_name = "gallery_crosscal_{0}".format(source)

                # create button for source
                html_code += """
                        <div class="w3-container">
                            <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-dark-gray w3-hover-gray w3-margin-bottom" onclick="show_hide_plots('{0:s}')">
                                {1:s}
                            </button>
                        </div>
                        <div class="w3-container w3-margin-bottom w3-hide" name="{0}">\n""".format(div_name, source)

                # beginning of table
                html_code += """
                    <div class="w3-container w3-center">
                        <div class="w3-responsive">
                            <table class="w3-table-all">\n"""

                # write the header
                html_code += """
                                <tr class="w3-amber">\n"""

                # fill header keys
                for key in table_keys:
                    # make sure that the beam is always there
                    if "beam" == key:
                        html_code += """<th>{}</th>\n""".format(
                            key)
                    elif keyword in key:
                        html_code += """<th>{}</th>\n""".format(
                            key.replace("ccal_", ""))

                # close table header
                html_code += """</tr>\n"""

                # go through the list for each beam
                for k in range(len(beam_list)):

                    # open row
                    html_code += """<tr>\n"""

                    # now go through keys and fill table
                    for key in table_keys:
                        if "beam" == key:
                            element = summary_table[key][k]
                        elif keyword in key:
                            element = summary_table[key][k]
                        # if it is neither the beam nor the key, continue
                        else:
                            continue

                        # check whether it is masked
                        if np.ma.is_masked(element):
                            html_code += """<td>-</td>\n"""
                        else:
                            html_code += """<td>{0}</td>\n""".format(element)

                    # close row
                    html_code += """</tr>\n"""

                # end of table
                html_code += """
                            </table>
                        </div>
                    </div>\n"""

                # closing the source button div
                html_code += """</div>\n"""
            else:
                if pos == 2:
                    logger.warning(
                        "Could not find polarised calibrator")
                    html_code += """
                        <div class="w3-container">
                            <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('{0:s}')">
                                {1:s}
                            </button>
                        </div>\n""".format(div_name, "Pol Calibrator")

        # closing the table button div
        html_code += """</div>\n"""
    else:
        logger.warning("No summary table available")
        html_code += """
                <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('gallery-1')">
                        Crosscal summary table
                    </button>
                </div>\n"""

    # Create html code for plots
    # ==========================

    # the different plots
    categories = ["BP_amp", "BP_phase", "Gain_amp", "Gain_phase", "K_", "Df_amp", "Df_phase", "Kcross", "Xf_amp",
                  "Xf_phase", "Raw_amp", "Raw_phase", "Model_amp", "Model_phase", "Corrected_amp", "Corrected_phase"]

    categories_titles = ["Bandpass Amplitude", "Bandpass Phase", "Gain factors Amplitude", "Gain factors Phase", "Global Delay", "Leakage Amplitude", "Leakage Phase", "Cross Hand Delay",
                         "Polarization Angle Amplitude", "Polarization Angle Phase", "Raw visibility Amplitude", "Raw Visibility Phase", "Model Amplitude", "Model Phase", "Corrected Amplitude", "Corrected Phase"]

    n_cats = len(categories)

    # get the images
    image_list = glob.glob(
        "{0:s}/{1:s}/*png".format(qa_report_obs_path, page_type))

    if len(image_list) != 0:
        # go throught the different types of plots
        for k in range(n_cats):

            # get list of plots for this category
            cat_plots = [pl for pl in image_list if categories[k] in pl]

            div_name = "gallery{0:d}".format(k)

            if len(cat_plots) != 0:

                # html_code += """<div class="plots">
                #     <button onclick="show_hide_plots()">
                #         <h3>{0:s}</h3>
                #     </button>\n""".format(categories_titles[k])

                # for image in cat_plots:
                #     html_code += """<div class="gallery" id="gallery">
                #             <a href="{0:s}">
                #                 <img src="{0:s}" alt="No image", width="100%">
                #             </a>
                #         </div>\n""".format(image)
                # html_code += """</div>\n"""

                html_code += """
                    <div class="w3-container">
                        <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('{0:s}')">
                            {1:s}
                        </button>
                    </div>
                    <div class="w3-container w3-margin-top w3-hide" name="{0:s}">\n""".format(div_name, categories_titles[k])

                img_counter = 0

                for image in cat_plots:
                    if img_counter % 3 == 0:
                        html_code += """<div class="w3-row">\n"""

                    html_code += """
                        <div class="w3-third">
                            <a href="{0:s}/{1:s}">
                                <img src="{0:s}/{1:s}" alt="No image", width="100%">
                            </a>
                        </div>\n""".format(page_type, os.path.basename(image))

                    if img_counter % 3 == 2 or img_counter == len(cat_plots)-1:
                        html_code += """</div>\n"""

                    img_counter += 1

                html_code += """</div>\n"""
            else:

                div_name = "gallery{0:d}".format(k)

                html_code += """
                    <div class="w3-container">
                        <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('{0:s}')">
                            {1:s}
                        </button>
                    </div>\n""".format(div_name, categories_titles[k])

                # html_code += """
                #     <div class="gallery" name="{0:s}">
                #         <p class="warning">
                #             No plots were found for {1:s}
                #         </p>
                #     </div>\n""".format(div_name, categories_titles[k])

    else:
        logger.warning("No crosscal plots found")
        html_code += """
        <div class="w3-container w3-large w3-text-red">
            <p>
                No plots were found for crosscal
            </p>
        </div>\n"""

    return html_code
