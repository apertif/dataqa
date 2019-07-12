import os
import sys
from astropy.table import Table, join
import logging
import glob
import time
import socket
import numpy as np

logger = logging.getLogger(__name__)


def write_obs_content_continuum(html_code, qa_report_obs_path, page_type, obs_info=None):
    """Function to create the html page for continuum

    Args:
        html_code (str): HTML code with header and title
        qa_report_obs_path (str): Path to the report directory
        page_type (str): The type of report page
        obs_info (list(str)): Basic information of observation

    Return:
        html_code (str): Body of HTML code for this page
    """

    logger.info("Writing html code for page {0:s}".format(page_type))

    html_code += """
        <div class="w3-container w3-large">
            <p>
                Here you can inspect for each beam the continuum image, PyBDSF diagnostic plots and the validation tool. The PyBDSF catalog is not accessible from this page, but can be found in the QA directory as a csv table.
                Of course, all of this only exists for beams with a continuum image created by the pipeline.<br>
                This page will only have content after the continuum QA step has been performed.
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

    # set the file name where information from the param*npy is stored
    continuum_summary_file = os.path.join(
        qa_report_obs_page_path, "{0}_{1}_summary.csv".format(obs_id, page_type))

    # set the file name where information of the image properties is stored
    continuum_image_properties_file = os.path.join(
        qa_report_obs_page_path, "continuum_image_properties.csv")

    if os.path.exists(continuum_summary_file):
        summary_table = Table.read(continuum_summary_file, format="ascii.csv")
    else:
        summary_table = None

    if os.path.exists(continuum_image_properties_file):
        image_properties_table = Table.read(
            continuum_image_properties_file, format="ascii.csv")
        if summary_table is None:
            summary_table = image_properties_table
        else:
            summary_table = join(
                summary_table, image_properties_table, keys='beam')

    # if there is a summary table
    # create tables for each source
    if summary_table is not None:

         # get the keys for the table
        table_keys = summary_table.keys()

        html_code += """
            <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('gallery-1')">
                        Continuum summary table
                    </button>
                </div>
            <div class="w3-container w3-margin-top w3-hide" name="gallery-1">\n"""

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
        logger.warning("No continuum table found")
        html_code += """
            <div class="w3-container">
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('gallery-1')">
                    Continuum summary table
                </button>
            </div>\n"""

    # get beams
    beam_list = glob.glob(
        "{0:s}/{1:s}/[0-3][0-9]".format(qa_report_obs_path, page_type))

    n_beams = len(beam_list)

    if n_beams != 0:

        beam_list.sort()

        beam_list = np.array(beam_list)

        # get a list of beam numbers
        beam_nr_list = np.array([os.path.basename(beam) for beam in beam_list])

        # get a list of reference beams
        beam_nr_list_ref = np.array(
            ["{0:02d}".format(beam) for beam in range(40)])

        # Create html code for continuum images gallery
        # =============================================

        # get a list of all images to make sure that at least one exists
        image_list = glob.glob(
            "{0:s}/{1:s}/[0-3][0-9]/image_mf_[0-9][0-9].png".format(qa_report_obs_path, page_type))

        if len(image_list) != 0:
            html_code += """
                <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('{0:s}')">{1:s}
                    </button>
                </div>
                <div class="w3-container w3-margin-top w3-hide" name="{0:s}">\n""".format("gallery_cont", "Continuum images")

            img_counter = 0

            for beam_nr in beam_nr_list_ref:

                # to properly make the gallery
                if img_counter % 4 == 0:
                    html_code += """<div class="w3-row">\n"""

                if beam_nr in beam_nr_list:
                    beam = beam_list[np.where(beam_nr_list == beam_nr)[0]][0]

                    # get the phase plots
                    image_list = glob.glob(os.path.join(
                        beam, "image_mf_[0-9][0-9].png"))

                    if len(image_list) != 0:
                        image = image_list[0]
                        image_exists = True
                    else:
                        image_exists = False

                else:
                    image_exists = False

                # if no image exists leave it empty
                if image_exists:
                    html_code += """
                    <div class="w3-quarter">
                        <a href="{0:s}/{1:s}/{2:s}">
                            <img src="{0:s}/{1:s}/{2:s}" alt="No image", width="100%">
                        </a>
                        <div class="w3-container w3-center">
                            <h5>Beam {1:s}</h5>
                        </div>
                    </div>\n""".format(page_type, os.path.basename(beam), os.path.basename(image))
                else:
                    html_code += """
                        <div class="w3-quarter">
                            <img src="" alt="No image for beam {0:s}", width="100%">
                        </div>\n""".format(beam_nr)

                if img_counter % 4 == 3 or img_counter == len(beam_nr_list_ref):
                    html_code += """</div>\n"""

                img_counter += 1

            html_code += """</div>\n"""
        else:
            html_code += """
                <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('{0:s}')">
                {1:s}
                    </button>
                </div>\n""".format("gallery_cont", "Continuum images")

        # Create html code for beam plots
        # ===============================

        for beam_nr in beam_nr_list_ref:

            button_html_name = "beam{0:s}".format(beam_nr)
            div_name = "continuum_gallery{0:s}".format(beam_nr)

            # get the diagnostic plots
            if beam_nr in beam_nr_list:
                image_list = glob.glob(
                    "{0:s}/*png".format(beam_list[np.where(beam_nr_list == beam_nr)[0]][0]))
            else:
                image_list = []

            n_images = len(image_list)

            if n_images != 0:

                image_list.sort()

                html_code += """
                        <div class="w3-container">
                            <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('{0:s}')">
                            Beam {1:s}
                            </button>
                        </div>
                        <div class="w3-container w3-margin-top w3-hide" name="{0:s}">
                            <div class="w3-container">
                                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-dark-gray w3-hover-gray w3-margin-bottom" class="button_continuum" onclick="show_hide_plots('{2:s}')">
                                    PyBDSF Diagnostic plots
                                </button>
                            </div>
                            <div class="w3-container w3-margin-top w3-hide" name="{2:s}">\n""".format(button_html_name, beam_nr, div_name)

                # go throught the different types of plots
                # they require a different layout because the plot sizes vary
                for m in range(n_images):

                    if m % 3 == 0:
                        html_code += """<div class="w3-row">\n"""

                    html_code += """
                        <div class="w3-third">
                            <a href="{0:s}/{1:s}/{2:s}">
                                <img src="{0:s}/{1:s}/{2:s}" alt="No image", width="100%">
                            </a>
                        </div>\n""".format(page_type, beam_nr, os.path.basename(image_list[m]))

                    if m % 3 == 2 or m == n_images-1:
                        html_code += """</div>\n"""

                html_code += """</div>\n"""

                # add the validation tool
                frame_name = glob.glob(
                    "{0:s}/*continuum_validation_pybdsf_snr5.0_int".format(beam_list[np.where(beam_nr_list == beam_nr)[0]][0]))

                if len(frame_name) != 0 and len(frame_name) == 1:
                    frame_name = frame_name[0]

                    if os.path.isdir(frame_name):

                        button_name = "validation_tool{0:s}".format(beam_nr)

                        html_code += """
                            <div class="w3-container">
                                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-dark-gray w3-hover-gray w3-margin-bottom" class="button_continuum" onclick="show_hide_plots('{0:s}')">
                                    Validation Tool
                                </button>
                            </div>
                            <div class="w3-container w3-margin-top w3-hide" name="{0:s}">\n""".format(button_name)

                        html_code += """
                                <div class="w3-container w3-large">
                                    <a href="{0:s}/{1:s}/{2:s}/index.html">Click here to open the validation tool</a> if it is not shown below
                                </div>
                                <div class="w3-container">
                                    <iframe class="w3-container" style="width:100%; height:1200px" src="{0:s}/{1:s}/{2:s}/index.html"></iframe>
                                </div>
                            </div>\n""".format(page_type, beam_nr, os.path.basename(frame_name))
                    else:
                        logger.warning("No continuum validation tool found for beam {0:s}".format(
                            beam_nr))
                        html_code += """
                            <div class="w3-container">
                                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-dark-gray w3-hover-gray w3-margin-bottom" class="button_continuum" onclick="show_hide_plots('{0:s}')">
                                    Validation Tool
                                </button>
                            </div>\n""".format(button_html_name)
                else:
                    logger.warning("No continuum validation tool found for beam {0:s}".format(
                        beam_nr))
                    html_code += """
                        <div class="w3-container">
                            <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-dark-gray w3-hover-gray w3-margin-bottom" class="button_continuum" onclick="show_hide_plots('{0:s}')">
                                Validation Tool
                            </button>
                        </div>\n""".format(button_html_name)

            else:
                logger.warning("No continuum plots and validation found for beam {0:s}".format(
                    beam_nr))
                html_code += """
                <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" class="disabled" onclick="show_hide_plots('{0:s}')">
                        Beam {1:s}
                    </button>
                </div>\n""".format(button_html_name, beam_nr)

            html_code += """</div>\n"""

            # html_code += """
            #     <div class="gallery" name="{0:s}">
            #         <p class="warning">
            #             No plots and validation tool were found for {1:s}
            #         </p>
            #     </div>\n""".format(button_html_name, page_type)

    else:
        logger.warning("No beams for continuum QA found")
        html_code += """
        <div class="w3-container w3-large w3-text-red">
            <p>
                No beams were found for continuum QA.
            </p>
        </div\n"""

    return html_code
