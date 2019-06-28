import os
import sys
from astropy.table import Table
import logging
import glob
import time
import socket
import numpy as np

logger = logging.getLogger(__name__)


def write_obs_content_mosaic(html_code, qa_report_obs_path, page_type):
    """Function to create the html page for mosaic
    """

    logger.info("Writing html code for page {0:s}".format(page_type))

    html_code += """
        <div class="w3-container w3-large">
            <p>
                Here you can inspect the continuum image, PyBDSF diagnostic plots and the validation tool for the mosaic of all available beam images. 
                The PyBDSF catalog is not accessible from this page, but can be found in the QA directory as a csv table.<br>
                This page will only have content after the mosaic was created and the mosaic QA step has been performed.
            </p>
        </div>\n
        """

    # get the diagnostic plots
    image_list = glob.glob(
        "{0:s}/{1:s}/*png".format(qa_report_obs_path, page_type))

    n_images = len(image_list)

    if n_images != 0:

        div_name = "gallery"

        html_code += """
                <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('{0:s}')">
                        PyBDSF Diagnostic plots
                    </button>
                </div>
                <div class="w3-container w3-margin-top w3-hide" name="gallery">\n""".format(div_name)

        # go throught the different types of plots
        # they require a different layout because the plot sizes vary
        for k in range(n_images):
            if k % 2 == 0:
                html_code += """
                <div class="w3-row">\n"""

            html_code += """
                <div class="w3-half">
                    <a href="{0:s}/{1:s}">
                        <img src="{0:s}/{1:s}" alt="No image", width="100%">
                    </a>
                </div>\n""".format(page_type, os.path.basename(image_list[k]))

            if k % 2 == 1 or k == n_images-1:
                html_code += """
                            </div>\n"""

        html_code += """
                    </div>\n"""

        # add the validation tool
        frame_name = glob.glob(
            "{0:s}/mosaic/*continuum_validation_pybdsf_snr5.0_int".format(qa_report_obs_path))

        if len(frame_name) != 0 and len(frame_name) == 1:
            frame_name = frame_name[0]

            if os.path.isdir(frame_name):

                button_name = "validation_tool"

                html_code += """
                    <div class="w3-container">
                        <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-dark-gray w3-hover-gray w3-margin-bottom"  onclick="show_hide_plots('{0:s}')">
                            Validation Tool
                        </button>
                    </div>
                    <div class="w3-container w3-margin-top w3-hide" name="{0:s}">\n""".format(button_name)

                html_code += """
                    <div class="w3-container w3-large">
                        <a href="{0:s}/{1:s}/index.html">Click here to open the validation tool</a> if it is not shown below
                    </div>
                    <div class="w3-container">
                        <iframe class="w3-container" style="width:100%; height:1200px" src="{0:s}/{1:s}/index.html"></iframe>
                    </div>
                    </div>\n""".format(page_type, os.path.basename(frame_name))
            else:
                logger.warning("No mosaic plots found")
                html_code += """
                <div class="w3-container w3-large w3-text-red">
                    <p>
                        No validation tool found for mosaic QA.
                    </p>
                </div>\n"""
        else:
            logger.warning("No mosaic plots found")
            html_code += """
            <div class="w3-container w3-large w3-text-red">
                <p>
                    No validation tool found for mosaic QA.
                </p>
            </div>\n"""

    else:
        logger.warning("No mosaic plots found")
        html_code += """
        <div class="w3-container w3-large w3-text-red">
            <p>
                No plot and validation tool found for mosaic QA.
            </p>
        </div>\n"""

    return html_code
