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
                    <tr>
                        <td>{0}</td>
                        <td>{1}</td>
                        <td>{2}</td>
                        <td>{3}</td>
                        <td>{4}</td>
                    </tr>
                </table>
            </div>
        </div>\n\n""".format(obs_id, target, fluxcal, polcal, osa)

    # Create html code for the osa report table
    # =========================================

    if osa_report != '':
        pass
        # check that osa report really exists:

        # if os.path.exist:
        #     obs_id = ""
        #     target = ""
        #     fluxcal = ""
        #     polcal = ""
        #     osa = ""
        # else:
        #     obs_id = obs_info['Obs_ID'][0]
        #     target = obs_info['Target'][0]
        #     fluxcal = obs_info['Flux_Calibrator'][0]
        #     polcal = obs_info['Pol_Calibrator'][0]
        #     osa = obs_info['OSA'][0]

        # html_code += """
        #     <div class="w3-container w3-center">
        #         <div class="w3-responsive">
        #             <table class="w3-table-all">
        #                 <tr class="w3-amber">
        #                     <th>Obs ID</th>
        #                     <th>Target</th>
        #                     <th>Flux calibrator</th>
        #                     <th>Pol calibrator</th>
        #                     <th>OSA</th>
        #                 </tr>
        #                     <td>{0:s}</td>
        #                     <td>{1:s}</td>
        #                     <td>{2:s}</td>
        #                     <td>{3:s}</td>
        #                     <td>{4:s}</td>
        #             </table>
        #         </div>
        #     </div>\n\n""".format(obs_id, target, fluxcal, polcal, osa)

    # Create html code for summary plot
    # =================================
    # get images
    image_list = glob.glob(
        "{0:s}/{1:s}/*.png".format(qa_report_obs_path, page_type))

    if len(image_list) != 0:

        # Make gallery for selfcal
        html_code += """
                <div class="w3-container w3-margin-top w3-show">
                    <h3> Selfcal CB plots </h3>
                    <p> These plots summarise the selfcal step of the pipeline for each of the compound beams. The left plot shows the beam numbers for reference. The middle and right plots refers to phase and amplitude selfcalibration, respectively. A missing beam would be gray. Amplitude selfcalibration is only turned on if the SNR is high enough. Phase selfcalibration is always done which is why only this plot shows if a beam failed on selfcal. Have a look at the selfcal page for further information on a given beam.</p>
                    <div class="w3-container w3-large">
                    \n"""

        for m in range(len(image_list)):

            image = image_list[m]

            if "cb_overview" in image or "selfcal" in image:

                if m % 3 == 0:
                    html_code += """<div class="w3-row">\n"""

                html_code += """
                    <div class="w3-third">
                        <a href="{0:s}/{1:s}">
                            <img src="{0:s}/{1:s}" alt="No image" style="width:100%">
                        </a>
                        <div class="w3-container w3-center">
                            <h5>Summary plot</h5>
                        </div>
                    </div>\n""".format(page_type, os.path.basename(image))

                if m % 3 == 2 or m == len(image_list)-1:
                    html_code += """</div>\n"""

        html_code += """
                    </div>
                </div>\n"""

        # Make gallery for continuum
        html_code += """
                <div class="w3-container w3-margin-top w3-show">
                    <h3> Continuum CB plots </h3>
                    <p> These plots summarise the continuum step of the pipeline for each of the compound beams. The left plot shows the beam numbers for reference. The middle and right plots gives the continuum rms and minor beam axis, respectively. A missing beam would be gray. Red indicates the beam has failed if the rms is above 50mJy/beam or the minor axis above 15arcsec. Have a look at the continuum page for further information on a given beam and the image gallery from all beams.</p>
                    <div class="w3-container w3-large">
                    \n"""

        image_counter = 0

        for image in image_list:

            if "cb_overview" in image or "continuum" in image:

                if image_counter % 3 == 0:
                    html_code += """<div class="w3-row">\n"""

                html_code += """
                    <div class="w3-third">
                        <a href="{0:s}/{1:s}">
                            <img src="{0:s}/{1:s}" alt="No image" style="width:100%">
                        </a>
                        <div class="w3-container w3-center">
                            <h5>Summary plot</h5>
                        </div>
                    </div>\n""".format(page_type, os.path.basename(image))

                if image_counter % 3 == 2 or m == len(image_list)-1:
                    html_code += """</div>\n"""

                image_counter += 1

        html_code += """
                    </div>
                </div>\n"""

        # Make gallery for continuum
        html_code += """
                <div class="w3-container w3-margin-top w3-show">
                    <h3> Line </h3>
                    <p> No plots available yet.</p>
                </div>
                    \n"""

        # for m in range(len(image_list)):

        #     image = image_list[m]

        #     if "cb_plots" in image or "continuum" in image:

        #         if m % 3 == 0:
        #             html_code += """<div class="w3-row">\n"""

        #         html_code += """
        #             <div class="w3-half">
        #                 <a href="{0:s}/{1:s}">
        #                     <img src="{0:s}/{1:s}" alt="No image" style="width:100%">
        #                 </a>
        #                 <div class="w3-container w3-center">
        #                     <h5>Summary plot</h5>
        #                 </div>
        #             </div>\n""".format(page_type, os.path.basename(image))

        #         if m % 3 == 2 or m == len(image_list)-1:
        #             html_code += """</div>\n"""

        # html_code += """
        #             </div>
        #         </div>\n"""

    else:
        logger.warning("No summary plots found")
        html_code += """
        <div class="w3-container w3-large w3-text-red">
            <p>
                No plots were found for summary
            </p>
        </div>\n"""

    return html_code
