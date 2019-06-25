import os
import sys
from astropy.table import Table
import logging
import glob
import time
import socket
import numpy as np

logger = logging.getLogger(__name__)


def write_obs_content_observing_log(html_code, qa_report_obs_path, page_type):
    """Function to create the html page for the observing log

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
            <p>Here you will find information from the future observing log which is not yet available.</p>
        </div>\n
        """

    # # Create html code for inspection plots
    # # =====================================
    # # get images
    # image_list = glob.glob(
    #     "{0:s}/{1:s}/*.png".format(qa_report_obs_path, page_type))

    # if len(image_list) != 0:
    #     html_code += """
    #             <div class="w3-container w3-margin-top w3-show">\n"""

    #     for image in image_list:
    #         html_code += """
    #             <div class="w3-half">
    #                 <a href="{0:s}/{1:s}">
    #                     <img src="{0:s}/{1:s}" alt="No image" style="width:100%">
    #                 </a>
    #                 <div class="w3-container w3-center">
    #                     <h5>Summary plot</h5>
    #                 </div>
    #             </div>\n""".format(page_type, os.path.basename(image))
    #     html_code += """</div>\n"""
    # else:
    #     logger.warning("No summary plot found found")
    #     html_code += """
    #     <div class="w3-container w3-large w3-text-red">
    #         <p>
    #             No plots were found for summary
    #         </p>
    #     </div>\n"""

    return html_code
