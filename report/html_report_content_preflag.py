import os
import sys
from astropy.table import Table
import logging
import glob
import time
import socket
import numpy as np

logger = logging.getLogger(__name__)


def write_obs_content_preflag(html_code, qa_report_obs_path, page_type, obs_info=None):
    """Function to create the html page for preflag

    Args:
        html_code (str): HTML code with header and title
        qa_report_obs_path (str): Path to the report directory
        page_type (str): The type of report page
        obs_id (str): ID of Observation

    Return:
        html_code (str): Body of HTML code for this page
    """

    logger.info("Writing html code for page {0:s}".format(page_type))

    html_code += """
        <div class="w3-container w3-large w3-margin-bottom">
            <p>This page provides information on the performance of the preflag module. You can find the following information here:</p>
            <div class="w3-container w3-large">
                1. Table of the preflag parameters for each source. In the current version of preflag, the parameters should all be identical for the calibrators and target. So, it is usually sufficient to look at the output from the target.<br>
                2. The preflag plots from the different beams compound into one plot per source and baseline.<br>
                3. The preflag plots for each beam individually.<br>
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
    preflag_summary_file = os.path.join(
        qa_report_obs_page_path, "{0}_{1}_summary.csv".format(obs_id, page_type))

    if os.path.exists(preflag_summary_file):
        summary_table = Table.read(preflag_summary_file, format="ascii.csv")

        # check if a source list already exists
        if source_list is None:
            source_list = np.unique(summary_table['source'])
    else:
        summary_table = None

    # if there is a summary table
    # create tables for each source
    if summary_table is not None:

        # get the keys for the table
        table_keys = summary_table.keys()
        # remove the source key as it is not necessary
        table_keys.remove('source')

        # button for table
        html_code += """
            <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('gallery-2')">
                        Preflag summary table
                    </button>
                </div>
            <div class="w3-container w3-margin-top w3-hide" name="gallery-2">\n"""

        for source in source_list:

            # get the rows for a given source
            summary_table_src = summary_table[summary_table['source'] == source]

            div_name = "gallery_preflag_{0}".format(source)

            if len(summary_table_src) != 0:

                beam_list = summary_table_src['beam']

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
                    html_code += """<th>{}</th>\n""".format(
                        key.replace("preflag_", "").replace("targetbeams_", ""))

                # close table header
                html_code += """</tr>\n"""

                # go through the list for each beam
                for k in range(len(beam_list)):

                    # open row
                    html_code += """<tr>\n"""

                    # now go through keys and fill table
                    for key in table_keys:
                        element = summary_table_src[key][k]

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
                logger.warning(
                    "Could not find entries for source {}".format(source))
                html_code += """
                    <div class="w3-container">
                        <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('{0:s}')">
                            {1:s}
                        </button>
                    </div>\n""".format(div_name, source)

        # closing the table button div
        html_code += """</div>\n"""
    else:
        logger.warning("No summary table available")
        html_code += """
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('gallery-2')">
                    Preflag summary table
                </button>\n"""

    # Create html code for combined preflag plots
    # ===========================================
    # get images
    image_list = glob.glob(
        "{0:s}/{1:s}/*.png".format(qa_report_obs_path, page_type))

    if len(image_list) != 0:
        html_code += """
                <div class="w3-container">
                        <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('gallery-1')">
                            Combined plots
                        </button>
                    </div>
                <div class="w3-container w3-margin-top w3-hide" name="gallery-1">\n"""

        img_counter = 0

        for image in image_list:
            if img_counter % 3 == 0:
                html_code += """<div class="w3-row">\n"""

            html_code += """
                <div class="w3-third">
                    <a href="{0:s}/{1:s}">
                        <img src="{0:s}/{1:s}" alt="No image" style="width:100%">
                    </a>
                    <!-- <div class="w3-container w3-center">
                        <h5>{1:s}</h5>
                    </div> --!>
                </div>\n""".format(page_type, os.path.basename(image))

            if img_counter % 3 == 2 or img_counter == len(image_list)-1:
                html_code += """</div>\n"""

            img_counter += 1

        html_code += """</div>\n"""
    else:
        logger.warning("No combined preflag plots found")
        html_code += """
            <div class="w3-container">
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('gallery-1')">
                    Combined plots
                </button>
            </div>\n"""

    # Create html code for individual beam plots
    # ==========================================

    # get beams
    beam_list = glob.glob(
        "{0:s}/{1:s}/[0-3][0-9]".format(qa_report_obs_path, page_type))

    n_beams = len(beam_list)

    # if there are beams go through them
    if n_beams != 0:

        beam_list.sort()

        for k in range(n_beams):

            # get the images
            images_in_beam = glob.glob("{0:s}/*png".format(beam_list[k]))

            div_name = "gallery{0:d}".format(k)

            if len(images_in_beam) != 0:

                images_in_beam.sort()

                html_code += """
                    <div class="w3-container">
                        <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('{0:s}')">
                            Beam {1:s}
                        </button>
                    </div>
                    <div class="w3-container w3-margin-top w3-hide" name="{0:s}">\n""".format(div_name, os.path.basename(beam_list[k]))

                img_counter = 0

                for image in images_in_beam:
                    if img_counter % 3 == 0:
                        html_code += """<div class="w3-row">\n"""

                    html_code += """
                        <div class="w3-third">
                            <a href="{0:s}/{1:s}/{2:s}">
                                <img src="{0:s}/{1:s}/{2:s}" alt="No image" style="width:100%">
                            </a>
                            <div class="w3-container w3-center">
                                <h5>{2:s}</h5>
                            </div>
                        </div>\n""".format(page_type, os.path.basename(beam_list[k]), os.path.basename(image))

                    if img_counter % 3 == 2 or img_counter == len(images_in_beam)-1:
                        html_code += """</div>\n"""

                    img_counter += 1

                html_code += """</div>\n"""
            else:
                logger.warning("No images in beam {0:s} found".format(
                    beam_list[k]))

                html_code += """
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('{0:s}')">
                        Beam {1:s}
                    </button>\n""".format(div_name, os.path.basename(beam_list[k]))

                # html_code += """
                #     <div class="gallery" name="{0:s}">
                #         <p class="warning">
                #             No plots were found for {1:s}
                #         </p>
                #     </div>\n""".format(div_name, page_type)
    else:
        logger.warning("No beams found for preflag found")
        html_code += """
        <div class="w3-container w3-large w3-text-red">
            <p>
                No plots were found for preflag
            </p>
        </div>\n"""

    return html_code
