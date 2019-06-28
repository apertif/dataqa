import os
import sys
from astropy.table import Table
import logging
import glob
import time
import socket
import numpy as np

logger = logging.getLogger(__name__)


def write_obs_content_inspection_plots(html_code, qa_report_obs_path, page_type, obs_info=None):
    """Function to create the html page for inspection plots

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
            <p>Here you can go through the inspection plots.</p>
        </div>\n
        """

    qa_report_obs_path_page = os.path.join(qa_report_obs_path, page_type)

    # Create html code for inspection plots
    # =====================================
    # assume that they are in the main directory if no obs infor are given
    if obs_info is None:

        # get images
        image_list = glob.glob(os.path.join(qa_report_obs_path_page, "*.png"))

        if len(image_list) != 0:

            # sort the list
            image_list.sort()

            html_code += """
                    <div class="w3-container w3-margin-top">\n"""

            img_counter = 0

            for image in image_list:
                if img_counter % 4 == 0:
                    html_code += """<div class="w3-row">\n"""

                html_code += """
                    <div class="w3-quarter">
                        <a href="{0:s}/{1:s}">
                            <img src="{0:s}/{1:s}" alt="No image" style="width:100%">
                        </a>
                        <!--<div class="w3-container w3-center">
                            <h5>{1:s}</h5>
                        </div>--!>
                    </div>\n""".format(page_type, os.path.basename(image))

                if img_counter % 4 == 3 or img_counter == len(image_list)-1:
                    html_code += """</div>\n"""

                img_counter += 1

            html_code += """</div>\n"""
        else:
            logger.warning("No inspection plots found")
            html_code += """
            <div class="w3-container w3-large w3-text-red">
                <p>
                    No plots were found for preflag
                </p>
            </div>\n"""
    # otherwise use the information
    else:
        if obs_info['Pol_Calibrator'][0] == '':
            src_name = [obs_info['Target'][0], obs_info['Flux_Calibrator'][0]]
        else:
            src_name = [obs_info['Target'][0], obs_info['Flux_Calibrator']
                        [0], obs_info['Pol_Calibrator'][0]]

        # now go through the list of sources
        for src in src_name:

            qa_report_obs_path_page_src = os.path.join(
                qa_report_obs_path_page, src)

            button_src_name = "plot_{0:s}".format(src)

            # for the target get the images that are in the directory
            if src == obs_info['Target'][0]:

                image_list = glob.glob(os.path.join(
                    qa_report_obs_path_page_src, "*.png"))

                # check that there are actually images
                if len(image_list) != 0:

                    # sort the list
                    image_list.sort()

                    # create container for gallery
                    html_code += """
                           <div class="w3-container">
                                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('{0:s}')">
                                {1:s}
                                </button>
                            </div>
                            <div class="w3-container w3-margin-top">\n""".format(button_src_name, src)

                    # to count the plots for the gallery
                    img_counter = 0

                    # go through the images
                    for image in image_list:

                        # use 4 plots per row
                        if img_counter % 4 == 0:
                            html_code += """<div class="w3-row">\n"""

                        # no caption need for the image
                        html_code += """
                            <div class="w3-quarter">
                                <a href="{0:s}/{1:s}/{2:s}">
                                    <img src="{0:s}/{1:s}/{2:s}" alt="No image" style="width:100%">
                                </a>
                            </div>\n""".format(page_type, src, os.path.basename(image))

                        # to close a row after four images or when there are no more images
                        if img_counter % 4 == 3 or img_counter == len(image_list)-1:
                            html_code += """</div>\n"""

                        img_counter += 1

                    # close the gallery div
                    html_code += """</div>\n"""

                # otherwise create a disabled button
                else:
                    logger.warning("No inspection plots found for target {0}".format(
                        src))
                    html_code += """
                    <div class="w3-container">
                        <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" class="disabled" onclick="show_hide_plots('{0:s}')">
                            {1:s}
                        </button>
                    </div>\n""".format(button_src_name, src)

            # for the calibrator, the plots in beam directories
            else:

                # get a list of beams instead of getting all plots
                # because they will be separated in polarization
                beam_list = np.array(glob.glob(os.path.join(
                    qa_report_obs_path_page_src, "[0-3][0-9]")))

                # check that there are images
                if len(beam_list) != 0:

                    # an array of just the beams
                    beam_nr_list = np.array(
                        [os.path.basename(beam) for beam in beam_list])

                    # a reference list of beams
                    beam_nr_list_ref = np.array(
                        ['{0:02d}'.format(beam) for beam in range(40)])

                    # the list of polarisation of the plots
                    pol_list = ['xx', 'yy']

                    html_code += """
                            <div class="w3-container">
                                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('{0:s}')">
                                {1:s}
                                </button>
                            </div>
                            <div class="w3-container w3-margin-top w3-hide" name="{0:s}">\n""".format(button_src_name, src)

                    # now go through each of the polarisations
                    for pol in pol_list:
                        div_name_pol = "insplot_gallery_{0:s}".format(pol)

                        # get a list of images
                        image_list = np.array(glob.glob(os.path.join(
                            qa_report_obs_path_page_src, "[0-3][0-9]/*{}.png".format(pol))))

                        # check that there are images
                        if len(image_list) != 0:

                            html_code += """
                                    <div class="w3-container">
                                        <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-dark-gray w3-hover-gray w3-margin-bottom" class="button_continuum" onclick="show_hide_plots('{0:s}')">
                                            {1:s}
                                        </button>
                                    </div>
                                    <div class="w3-container w3-margin-top w3-hide" name="{0:s}">\n""".format(div_name_pol, pol)

                            img_counter = 0

                            # go through all reference beams
                            for beam_nr in beam_nr_list_ref:

                                # to properly make the gallery with 5 images in a row
                                if img_counter % 5 == 0:
                                    html_code += """<div class="w3-row">\n"""

                                # get the image from the list if one exists for this beam
                                if beam_nr in beam_nr_list:
                                    image = image_list[np.where(
                                        beam_nr_list == beam_nr)[0]][0]
                                    image_exists = True
                                else:
                                    image_exists = False

                                # if there is an image plot it
                                if image_exists:
                                    html_code += """
                                        <div class="w3-quarter">
                                            <a href="{0:s}/{1:s}/{2:s}/{3:s}">
                                                <img src="{0:s}/{1:s}/{2:s}/{3:s}" alt="No image", width="100%">
                                            </a>
                                            <div class="w3-container w3-center">
                                                <h5>Beam {1:s}</h5>
                                            </div>
                                        </div>\n""".format(page_type, src, beam_nr, os.path.basename(image))
                                # if not put an empty one there
                                else:
                                    html_code += """
                                        <div class="w3-quarter">
                                            <img src="" alt="No image for beam {0:s}", width="100%">
                                        </div>\n""".format(beam_nr)

                                # closing the row
                                if img_counter % 5 == 4 or img_counter == len(beam_nr_list_ref):
                                    html_code += """</div>\n"""

                                img_counter += 1

                            # close div for this plot
                            html_code += """</div>\n"""

                        # add a disabled button
                        else:
                            logging.warning(
                                "No plots found for polarisation {}".format(pol))
                            html_code += """
                            <div class="w3-container">
                                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-dark-gray w3-hover-gray w3-margin-bottom" class="button_continuum" onclick="show_hide_plots('{0:s}')">
                                    {1:s}
                                </button>
                            </div>\n""".format(div_name_pol, pol)

                    html_code += """
                            </div>\n"""

                # otherwise create a disabled button
                else:
                    logger.warning("No inspection plots found for calibrator {0}".format(
                        src))
                    html_code += """
                    <div class = "w3-container" >
                        <button class = "w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" class = "disabled" onclick = "show_hide_plots('{0:s}')" >
                            {1: s}
                        </button >
                    </div >\n""".format(button_src_name, src)

    return html_code
