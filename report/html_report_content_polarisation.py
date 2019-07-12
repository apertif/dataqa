import os
import sys
from astropy.table import Table
import logging
import glob
import time
import socket
import numpy as np

logger = logging.getLogger(__name__)


def write_obs_content_polarisation(html_code, qa_report_obs_path, page_type, obs_info=None):
    """Function to create the html page for polarisation

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
                This page will provide information on the performance of the polarisation module. The content of the polarisation QA has not been defined yet<br>
            </p>
        </div>\n
        """

    return html_code
