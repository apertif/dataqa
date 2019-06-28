import os
import sys
from astropy.table import Table
import logging
import glob
import time
import socket
import numpy as np

logger = logging.getLogger(__name__)


def write_obs_content_crosscal(html_code, qa_report_obs_path, page_type):
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
                Here you can go through the different plots created by crosscal.
            </p>
        </div>\n
        """

    # Create html code for summary table
    # ==================================

    table_found = True

    if table_found:
        html_code += """
            <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('gallery-1')">
                        Crosscal summary table
                    </button>
                </div>
            <div class="w3-container w3-margin-top w3-show" name="gallery-1">\n"""

        html_code += """
            <p> No table here yet.
            </p>\n"""
        html_code += """</div>\n"""
    else:
        logger.warning("No combined crosscal plots found")
        html_code += """
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('gallery-1')">
                    Crosscal summary table
                </button>\n"""

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
