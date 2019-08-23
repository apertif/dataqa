import os
import sys
from astropy.table import Table
import logging
import glob
import time
import socket
import numpy as np

logger = logging.getLogger(__name__)


def write_obs_content_line(html_code, qa_report_obs_path, page_type):
    """Function to create the html page for line

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
                This page provides information on the performance of the line module. You can find the following information here: 
            </p>
            <div class="w3-container w3-large">
                1. A summary table (not yet available)<br>
                2. For each cube, the spectra of the channal rms per beam. This allows you to look for difference between beams<br>
                3. For each beam, the spectra of the channal rms per cube. <br>
            </div>
        </div>\n
        """

    # Create html code for summary table
    # ==================================

    table_found = False

    if table_found:
        html_code += """
            <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('gallery-1')">
                        Line summary table
                    </button>
                </div>
            <div class="w3-container w3-margin-top w3-show" name="gallery-1">\n"""

        html_code += """
            <p> No table here yet.
            </p>\n"""
        html_code += """</div>\n"""
    else:
        logger.warning("No line table found")
        html_code += """
            <div class="w3-container">
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('gallery-1')">
                    Line summary table
                </button>
            </div>\n"""

    # Create html code for cube gallery
    # =================================

    # get beams
    beam_list = glob.glob(
        "{0:s}/{1:s}/[0-3][0-9]".format(qa_report_obs_path, page_type))

    # total number of expected beams
    n_beams = 40

    # total number of expected cubes per beam
    n_cubes = 8

    if beam_list != 0:

        html_code += """
            <div class="w3-container">
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('{0:s}')">{1:s}
                </button>
            </div>
            <div class="w3-container w3-margin-top w3-hide" name="{0:s}">\n""".format("gallery_cubes", "Cubes")

        # go through the list of cubes
        for cube_counter in range(n_cubes):

            # get a list of cubes
            cube_list = glob.glob(
                "{0:s}/{1:s}/[0-3][0-9]/*cube{2:d}*.png".format(qa_report_obs_path, page_type, cube_counter))

            div_name = "gallery_cube_{0}".format(cube_counter)

            # if there plots for this cube, create the gallery
            if len(cube_list) != 0:

                cube_list.sort()

                cube_list = np.array(cube_list)

                # create button for source
                html_code += """
                        <div class="w3-container">
                            <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-dark-gray w3-hover-gray w3-margin-bottom" onclick="show_hide_plots('{0:s}')">
                                Cube {1:d}
                            </button>
                        </div>
                        <div class="w3-container w3-margin-bottom w3-hide" name="{0}">\n""".format(div_name, cube_counter)

                # get a list of beams with cubes
                beam_list = np.array(
                    [int(os.path.dirname(cube).split("/")[-1]) for cube in cube_list])

                for beam_nr in range(n_beams):

                    image = cube_list[np.where(beam_list == beam_nr)]

                    if beam_nr % 5 == 0:
                        html_code += """<div class="w3-row">\n"""

                    # if there is a cube for this beam add it to gallery
                    if len(image) != 0:
                        html_code += """
                                <div class="w3-col w3-border" style="width:20%">
                                    <a href="{0:s}/{1:02d}/{2:s}">
                                        <img src="{0:s}/{1:02d}/{2:s}" alt="No image for beam {1:02d}", width="100%">
                                    </a>
                                    <div class="w3-container"><h5>Beam {1:02d}</h5></div>
                                </div>\n""".format(page_type, beam_nr, os.path.basename(image[0]))
                    # otherwise keep it empty
                    else:
                        html_code += """
                                <div class="w3-col" style="width:20%">
                                    <a href="#">
                                        <img src="#" alt="No image for beam {0:02d}", width="100%">
                                    </a>
                                </div>\n""".format(beam_nr)

                    if beam_nr % 5 == 4 or beam_nr == n_beams-1:
                        html_code += """</div>\n"""

                html_code += """</div>\n"""
            else:
                html_code += """
                        <div class="w3-container">
                            <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('{0:s}')">
                                Cube {1:d}
                            </button>
                        </div>\n""".format(div_name, cube_counter)

        html_code += """</div>\n"""
    else:
        logger.warning("No beams found for line cube gallery")
        html_code += """
            <div class="w3-container">
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('{0:s}')">
            {1:s}
                </button>
            </div>\n""".format("gallery_cubes", "Cubes")

    # Create html code for image gallery
    # ==================================

    # get beams
    beam_list = glob.glob(
        "{0:s}/{1:s}/[0-3][0-9]".format(qa_report_obs_path, page_type))

    n_beams = len(beam_list)

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

                    if img_counter % 4 == 0:
                        html_code += """<div class="w3-row">\n"""

                    html_code += """
                        <div class="w3-quarter w3-border">
                            <a href="{0:s}/{1:s}/{2:s}">
                                <img src="{0:s}/{1:s}/{2:s}" alt="No cube available for beam {1:s}", width="100%">
                            </a>
                            <div class="w3-container w3-center"><h5>{2:s}</h5></div>
                        </div>\n""".format(page_type, os.path.basename(beam_list[k]), os.path.basename(image))

                    if img_counter % 4 == 3 or img_counter == len(images_in_beam) - 1:
                        html_code += """</div>\n"""

                    img_counter += 1

                html_code += """</div>\n"""
            else:
                logger.warning("No plot for cube in beam {0:s} found".format(
                    beam_list[k]))

                html_code += """
                    <div class="w3-container">
                        <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('{0:s}')">
                            Beam {1:s}
                        </button>
                    </div>\n""".format(div_name, os.path.basename(beam_list[k]))

                # html_code += """
                #     <div class="gallery" name="{0:s}">
                #         <p class="warning">
                #             No plots were found for {1:s}
                #         </p>
                #     </div>\n""".format(div_name, page_type)
    else:
        logger.warning("No beams found for cube found")
        html_code += """
        <div class="w3-container w3-large w3-text-red">
            <p>
                No plots were found for cube
            </p>
        </div>\n"""

    # html_code += """
    #     <p class="info">
    #         The overview does not cover line QA yet
    #     </p>\n0
    #     """

    return html_code
