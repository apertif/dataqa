import os
import sys
from astropy.table import Table
import logging
import glob
import time
import socket
import numpy as np

logger = logging.getLogger(__name__)


def write_obs_content_preflag(html_code, qa_report_obs_path, page_type):
    """Function to create the html page for preflag

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
            <p>Here you can go through the different plots created by preflag.</p>
        </div>\n
        """

    # Create html code for summary table
    # ==================================

    table_found = True

    if table_found:
        html_code += """
            <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('gallery-2')">
                        Preflag summary table
                    </button>
                </div>
            <div class="w3-container w3-margin-top w3-show" name="gallery-2">\n"""

        html_code += """
            <p> No table here yet.
            </p>\n"""
        html_code += """</div>\n"""
    else:
        logger.warning("No combined preflag plots found")
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
