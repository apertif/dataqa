import os
import sys
from astropy.table import Table
import logging
import glob
import time
import socket
import numpy as np

logger = logging.getLogger(__name__)


def write_obs_content_selfcal(html_code, qa_report_obs_path, page_type, obs_info=None):
    """Function to create the html page for selfcal

    Args:
        html_code (str): HTML code with header and title
        qa_report_obs_path (str): Path to the report directory
        page_type (str): The type of report page
        obs_info (list(str)): Basic information from observation

    Return:
        html_code (str): Body of HTML code for this page
    """

    logger.info("Writing html code for page {0:s}".format(page_type))

    html_code += """
        <div class="w3-container w3-large">
            <p>
                This page shows the images and residuals from every major and minor phase self-cal iteration.
                In addition selfcal phase and amplitude gains are shown for each antenna. <br>
                This page will only have content after the selfcal QA step has been performed.
            </p>
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
                        Selfcal summary table
                    </button>
                </div>
            <div class="w3-container w3-margin-top w3-show" name="gallery-1">\n"""

        beam_list = summary_table['beam']

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
            html_code += """<th>{}</th>\n""".format(
                key.replace("targetbeams_", ""))

        # close table header
        html_code += """</tr>\n"""

        for k in range(len(beam_list)):

            # open row
            html_code += """<tr>\n"""

            # now go through keys and fill table
            for key in table_keys:

                # get the element from table
                element = summary_table[key][k]

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

        html_code += """</div>\n"""
    else:
        logger.warning("No selfcal table found")
        html_code += """
            <div class="w3-container">
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('gallery-1')">
                    Selfcal summary table
                </button>
            </div>\n"""

    # the plots for the selfcal gains
    # ===============================

    # get the phase plots
    phase_list = glob.glob(
        "{0:s}/{1:s}/SCAL_phase*png".format(qa_report_obs_path, page_type))

    if len(phase_list) != 0:
        html_code += """
            <div class="w3-container">
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('{0:s}')">{1:s}
                </button>
            </div>
            <div class="w3-container w3-margin-top w3-hide" name="{0:s}">\n""".format("gallery_phase", "Gain factors Phase")

        img_counter = 0

        for image in phase_list:

            if img_counter % 3 == 0:
                html_code += """<div class="w3-row">\n"""

            html_code += """
            <div class="w3-third">
                <a href="{0:s}/{1:s}">
                <img src="{0:s}/{1:s}" alt="No image", width="100%">
                </a>
            </div>\n""".format(page_type, os.path.basename(image))

            if img_counter % 3 == 2:
                html_code += """</div>\n"""

            img_counter += 1

        html_code += """</div>\n"""
    else:
        html_code += """
            <div class="w3-container">
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('{0:s}')">
            {1:s}
                </button>
            </div>\n""".format("gallery_phase", "Gain factors Phase")

    # get the amplitude plots
    amp_list = glob.glob(
        "{0:s}/{1:s}/SCAL_amp*png".format(qa_report_obs_path, page_type))

    if len(amp_list) != 0:
        html_code += """
            <div class="w3-container">
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('{0:s}')">{1:s}
                </button>
            </div>
            <div class="w3-container w3-margin-top w3-hide" name="{0:s}">\n""".format("gallery_amp", "Gain factors Amplitude")

        img_counter = 0

        for image in amp_list:

            if img_counter % 3 == 0:
                html_code += """<div class="w3-row">\n"""

            html_code += """
                <div class="third">
                    <a href="{0:s}/{1:s}">
                    <img src="{0:s}/{1:s}" alt="No image", width="100%">
                    </a>
                </div>\n""".format(page_type, os.path.basename(image))

            if img_counter % 3 == 2:
                html_code += """</div>\n"""

            img_counter += 1

        html_code += """</div>\n"""
    else:
        html_code += """
                <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('{0:s}')">
                        {1:s}
                    </button>
                </div>\n""".format("gallery_amp", "Gain factors Amplitude")

    # Selfcal iteration maps sorted by beam
    # =====================================

    # get beams
    beam_list = glob.glob(
        "{0:s}/{1:s}/[0-3][0-9]".format(qa_report_obs_path, page_type))

    n_beams = len(beam_list)

    if n_beams != 0:

        beam_list.sort()

        for k in range(n_beams):

            button_html_name = "beam{0:d}".format(k)
            div_name = "gallery{0:d}".format(k)

            # get the diagnostic plots
            image_list = glob.glob("{0:s}/*png".format(beam_list[k]))

            n_images = len(image_list)

            if n_images != 0:

                image_list.sort()

                html_code += """
                    <div class="w3-container">
                        <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('{0:s}')">
                        Beam {1:s}
                        </button>
                    </div>
                    <div class="w3-container w3-margin-top w3-hide" name="{0:s}">\n""".format(div_name, os.path.basename(beam_list[k]))

                img_counter = 0

                for image in image_list:

                    major_cycle = os.path.basename(image).split("_")[0]

                    minor_cycle = os.path.basename(image).split("_")[1]

                    image_type = os.path.basename(image).split(".")[
                        0].split("_")[-1]

                    if image_type == "image":
                        caption = "Image: major {0:s}, minor {1:s}".format(
                            major_cycle, minor_cycle)
                    elif image_type == "residual":
                        caption = "Residual: major {0:s}, minor {1:s}".format(
                            major_cycle, minor_cycle)
                    else:
                        caption = ""

                    if img_counter % 4 == 0:
                        html_code += """<div class="w3-row">\n"""

                    html_code += """
                        <div class="w3-quarter">
                            <a href="{0:s}/{1:s}/{2:s}">
                                <img src="{0:s}/{1:s}/{2:s}" alt="No image", width="100%">
                            </a>
                            <div class="w3-container"><h5>{3:s}</h5></div>
                        </div>\n""".format(page_type, os.path.basename(beam_list[k]), os.path.basename(image), caption)

                    if img_counter % 4 == 3 or img_counter == n_images-1:
                        html_code += """</div>\n"""

                    img_counter += 1

                html_code += """</div>\n"""

                # # go throught the different types of plots
                # # they require a different layout because the plot sizes vary
                # html_code += """<div class="gallery_column" name="{0:s}">\n""".format(
                # div_name)
                # for m in range(n_images):
                #     if m % 4 == 0:
                #         html_code += """<div class="gallery_row">"""

                #     html_code += """<div class="mosaic_img">
                #             <a href="{0:s}/{1:s}/{2:s}">
                #                 <img src="{0:s}/{1:s}/{2:s}" alt="No image", width="100%">
                #             </a>
                #         </div>\n""".format(page_type, os.path.basename(beam_list[k]), os.path.basename(image_list[m]))

                #     if m % 2 != 0 or m == n_images-1:
                #         html_code += """</div>\n"""

            else:
                logger.warning("No selfcal maps found in {0:s}".format(
                    os.path.basename(beam_list[k])))
                html_code += """
                <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" class="disabled" onclick="show_hide_plots('{0:s}')">
                        Beam {1:s}
                    </button>
                </div>\n""".format(button_html_name, os.path.basename(beam_list[k]))

    else:
        logger.warning("No beams for selfcal QA found")
        html_code += """
        <div class="w3-container w3-large w3-text-red">
            <p>
                No beams were found for selfcal QA.
            </p>
        </div>\n"""

    # html_code += """
    #     <p class="info">
    #         The overview does not cover selfcal QA yet
    #     </p>\n
    #     """

    return html_code
