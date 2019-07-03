import os
import sys
from astropy.table import Table
import logging
import glob
import time
import socket
import numpy as np

logger = logging.getLogger(__name__)


def write_obs_content_summary(html_code, qa_report_obs_path, page_type, obs_info=None, osa_report=''):
    """Function to create the html page for summary

    Args:
        html_code (str): HTML code with header and title
        qa_report_obs_path (str): Path to the report directory
        page_type (str): The type of report page
        obs_info (dict): Information about the observation
        add_osa_report (bool): To add the osa report

    Return:
        html_code (str): Body of HTML code for this page
    """

    logger.info("Writing html code for page {0:s}".format(page_type))

    html_code += """
        <div class="w3-container w3-large">
            <p>Here you will find a summary of the observation.</p>
        </div>\n
        """

    # Create html code for the summary table
    # ======================================

    if obs_info is None:
        obs_id = ""
        target = ""
        fluxcal = ""
        polcal = ""
        osa = ""
    else:
        obs_id = obs_info['Obs_ID'][0]
        target = obs_info['Target'][0]
        fluxcal = obs_info['Flux_Calibrator'][0]
        polcal = obs_info['Pol_Calibrator'][0]
        osa = obs_info['OSA'][0]

    html_code += """
        <div class="w3-container w3-center">
            <div class="w3-responsive">
                <table class="w3-table-all">
                    <tr class="w3-amber">
                        <th>Obs ID</th>
                        <th>Target</th>
                        <th>Flux calibrator</th>
                        <th>Pol calibrator</th>
                        <th>OSA</th>
                    </tr>
                        <td>{0:s}</td>
                        <td>{1:s}</td>
                        <td>{2:s}</td>
                        <td>{3:s}</td>
                        <td>{4:s}</td>
                </table>
            </div>
        </div>\n\n""".format(obs_id, target, fluxcal, polcal, osa)

    # Create html code for the osa repor table
    # ========================================

    if add_osa_report:
        # check that osa report really exists:

        if os.path.exist
        obs_id = ""
        target = ""
        fluxcal = ""
        polcal = ""
        osa = ""
    else:
        obs_id = obs_info['Obs_ID'][0]
        target = obs_info['Target'][0]
        fluxcal = obs_info['Flux_Calibrator'][0]
        polcal = obs_info['Pol_Calibrator'][0]
        osa = obs_info['OSA'][0]

    html_code += """
        <div class="w3-container w3-center">
            <div class="w3-responsive">
                <table class="w3-table-all">
                    <tr class="w3-amber">
                        <th>Obs ID</th>
                        <th>Target</th>
                        <th>Flux calibrator</th>
                        <th>Pol calibrator</th>
                        <th>OSA</th>
                    </tr>
                        <td>{0:s}</td>
                        <td>{1:s}</td>
                        <td>{2:s}</td>
                        <td>{3:s}</td>
                        <td>{4:s}</td>
                </table>
            </div>
        </div>\n\n""".format(obs_id, target, fluxcal, polcal, osa)

    # Create html code for summary plot
    # =================================
    # get images
    image_list = glob.glob(
        "{0:s}/{1:s}/*.png".format(qa_report_obs_path, page_type))

    if len(image_list) != 0:
        html_code += """
                <div class="w3-container w3-margin-top w3-show">
                    <div class="w3-container w3-large">
                        <p> This plot summarizes the observation and pipeline processing for each of the compound beams</p>
                    </div>\n"""

        for image in image_list:
            html_code += """
                <div class="w3-half">
                    <a href="{0:s}/{1:s}">
                        <img src="{0:s}/{1:s}" alt="No image" style="width:100%">
                    </a>
                    <div class="w3-container w3-center">
                        <h5>Summary plot</h5>
                    </div>
                </div>\n""".format(page_type, os.path.basename(image))
        html_code += """</div>\n"""
    else:
        logger.warning("No summary plot found found")
        html_code += """
        <div class="w3-container w3-large w3-text-red">
            <p>
                No plots were found for summary
            </p>
        </div>\n"""

    return html_code
