import os
import sys
from astropy.table import Table
import logging
import glob
import time
import socket
import numpy as np

logger = logging.getLogger(__name__)


def write_obs_content_inspection_plots(html_code, qa_report_obs_path, page_type):
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
            <p>Here you can go through the different plots created by preflag.</p>
        </div>\n
        """

    # Create html code for inspection plots
    # =====================================
    # get images
    image_list = glob.glob(
        "{0:s}/{1:s}/*.png".format(qa_report_obs_path, page_type))

    if len(image_list) != 0:
        html_code += """
                <div class="w3-container w3-margin-top">\n"""

        img_counter = 0

        for image in image_list:
            if img_counter % 3 == 0:
                html_code += """<div class="w3-row">\n"""

            html_code += """
                <div class="w3-third">
                    <a href="{0:s}/{1:s}">
                        <img src="{0:s}/{1:s}" alt="No image" style="width:100%">
                    </a>
                    <!--<div class="w3-container w3-center">
                        <h5>{1:s}</h5>
                    </div>--!>
                </div>\n""".format(page_type, os.path.basename(image))

            if img_counter % 3 == 2 or img_counter == len(image_list)-1:
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

    return html_code
