import os
import sys
from astropy.table import Table
import logging
import glob
import time
import socket
import numpy as np

logger = logging.getLogger(__name__)


def write_obs_content_selfcal(html_code, qa_report_obs_path, page_type, obs_info=None):
    """Function to create the html page for selfcal

    Args:
        html_code (str): HTML code with header and title
        qa_report_obs_path (str): Path to the report directory
        page_type (str): The type of report page
        obs_info (list(str)): Basic information from observation

    Return:
        html_code (str): Body of HTML code for this page
    """

    logger.info("Writing html code for page {0:s}".format(page_type))

    html_code += """
        <div class="w3-container w3-large">
            <p>
                This page provides information on the performance of the selfcal module. You can find the following information here: 
            </p>
            <div class="w3-container w3-large">
                1. Table of the selfcal parameters from the pipeline. For example, you can see for which beams amplitude calibration was turned on.<br>
                2. Plots of the self-calibration gain factors for amplitude and phase. These are the most important plots, you want to check. <br>
                3. Selfcal image from the the first and last cycle from each beam. If amplitude self-calibration is available, it is the chosen as the last cycle.<br>
                4. Selfcal residuals from the the first and last cycle from each beam. If amplitude self-calibration is available, it is the chosen as the last .cycle.<br>
                5. For each beam, plots of all selfcal images and residuals from phase and if available amplitude self-calibration.
            </div>
        </div>\n
        """

    qa_report_obs_page_path = os.path.join(qa_report_obs_path, page_type)

    # Create html code for summary table
    # ==================================

    if obs_info is not None:
        obs_id = obs_info['Obs_ID'][0]
        source_list = np.array(
            [obs_info['Target'][0], obs_info['Flux_Calibrator'][0], obs_info['Pol_Calibrator'][0]])
    else:
        obs_id = os.path.basename(qa_report_obs_path)
        source_list = None

    # set the file name
    crosscal_summary_file = os.path.join(
        qa_report_obs_page_path, "{0}_{1}_summary.csv".format(obs_id, page_type))

    if os.path.exists(crosscal_summary_file):
        summary_table = Table.read(crosscal_summary_file, format="ascii.csv")

    else:
        summary_table = None

    # if there is a summary table
    # create tables for each source
    if summary_table is not None:

        # get the keys for the table
        table_keys = summary_table.keys()

        html_code += """
            <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('gallery-1')">
                        Selfcal summary table
                    </button>
                </div>
            <div class="w3-container w3-margin-top w3-margin-bottom w3-hide" name="gallery-1">\n"""

        beam_list = summary_table['beam']

        # beginning of table
        html_code += """
                <div class="w3-container w3-center">
                    <div class="w3-responsive">
                        <table class="w3-table-all">\n"""

        # write the header
        html_code += """
                            <tr class="w3-amber">\n"""

        # fill header keys
        for key in table_keys:
            # make sure that the beam is always there
            html_code += """<th>{}</th>\n""".format(
                key.replace("targetbeams_", ""))

        # close table header
        html_code += """</tr>\n"""

        for k in range(len(beam_list)):

            # open row
            html_code += """<tr>\n"""

            # now go through keys and fill table
            for key in table_keys:

                # get the element from table
                element = summary_table[key][k]

                # check whether it is masked
                if np.ma.is_masked(element):
                    html_code += """<td>-</td>\n"""
                else:
                    html_code += """<td>{0}</td>\n""".format(element)

            # close row
            html_code += """</tr>\n"""

        # end of table
        html_code += """
                    </table>
                </div>
            </div>\n"""

        html_code += """</div>\n"""
    else:
        logger.warning("No selfcal table found")
        html_code += """
            <div class="w3-container">
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('gallery-1')">
                    Selfcal summary table
                </button>
            </div>\n"""

    # the plots for the selfcal gains
    # ===============================

    # get the phase plots
    phase_list = glob.glob(
        "{0:s}/{1:s}/SCAL_phase*png".format(qa_report_obs_path, page_type))

    if len(phase_list) != 0:
        html_code += """
            <div class="w3-container">
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('{0:s}')">{1:s}
                </button>
            </div>
            <div class="w3-container w3-margin-top w3-hide" name="{0:s}">\n""".format("gallery_phase", "Gain factors Phase")

        img_counter = 0

        for image in phase_list:

            if img_counter % 3 == 0:
                html_code += """<div class="w3-row">\n"""

            html_code += """
            <div class="w3-third">
                <a href="{0:s}/{1:s}">
                <img src="{0:s}/{1:s}" alt="No image", width="100%">
                </a>
            </div>\n""".format(page_type, os.path.basename(image))

            if img_counter % 3 == 2 or img_counter == len(phase_list)-1:
                html_code += """</div>\n"""

            img_counter += 1

        html_code += """</div>\n"""
    else:
        html_code += """
            <div class="w3-container">
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('{0:s}')">
            {1:s}
                </button>
            </div>\n""".format("gallery_phase", "Gain factors Phase")

    # get the amplitude plots
    amp_list = glob.glob(
        "{0:s}/{1:s}/SCAL_amp*png".format(qa_report_obs_path, page_type))

    if len(amp_list) != 0:
        html_code += """
            <div class="w3-container">
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('{0:s}')">{1:s}
                </button>
            </div>
            <div class="w3-container w3-margin-top w3-hide" name="{0:s}">\n""".format("gallery_amp", "Gain factors Amplitude")

        img_counter = 0

        for image in amp_list:

            if img_counter % 3 == 0:
                html_code += """<div class="w3-row">\n"""

            html_code += """
                <div class="w3-third">
                    <a href="{0:s}/{1:s}">
                    <img src="{0:s}/{1:s}" alt="No image", width="100%">
                    </a>
                </div>\n""".format(page_type, os.path.basename(image))

            if img_counter % 3 == 2 or img_counter == len(phase_list)-1:
                html_code += """</div>\n"""

            img_counter += 1

        html_code += """</div>\n"""
    else:
        html_code += """
                <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('{0:s}')">
                        {1:s}
                    </button>
                </div>\n""".format("gallery_amp", "Gain factors Amplitude")

    # Gallery of selfcal images
    # =========================

    # get beams
    beam_dir_list = glob.glob(
        "{0:s}/{1:s}/[0-3][0-9]".format(qa_report_obs_path, page_type))

    n_beams = 40

    image_list = ["" for k in range(2 * n_beams)]

    if len(beam_dir_list) != 0:

        beam_dir_list.sort()

        # go through the beams to get the image directory
        for k in range(len(beam_dir_list)):

            beam_dir = beam_dir_list[k]

            # get the beam which serves as the index for the image list
            beam = int(os.path.basename(beam_dir))

            # get amplitude selfcal images
            image_list_amp = glob.glob(
                "{0:s}/amplitude*image.png".format(beam_dir))
            image_list_amp.sort()

            # get phase selfcal images
            image_list_phase = glob.glob(
                "{0:s}/phase*image.png".format(beam_dir))
            image_list_phase.sort()

            # if there are no phase selfcal images, then there are no amplitude selfcal images
            if len(image_list_phase) != 0:

                # the first image is always from selfcal
                image_first = image_list_phase[0]

                # final selfcal image can be from amplitude selfcal
                if len(image_list_amp) != 0:
                    image_last = image_list_amp[-1]
                else:
                    image_last = image_list_phase[-1]

                # the first image has an even index
                image_list[2 * beam] = image_first
                # the laste image has an uneven index
                image_list[2 * beam + 1] = image_last

        # check that the list of images is not empty
        if len(np.unique(image_list)) != 1:

            html_code += """
                <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('{0:s}')">{1:s}
                    </button>
                </div>
                <div class="w3-container w3-margin-top w3-hide" name="{0:s}">\n""".format("gallery_images", "Selfcal images")

            img_counter = 0

            beam_counter = 0

            for k in range(len(image_list)):

                # count one beam every second image
                if k != 0 and k % 2 == 0:
                    beam_counter += 1

                image = image_list[k]

                if img_counter % 4 == 0:
                    html_code += """<div class="w3-row">\n"""

                html_code += """
                        <div class="w3-quarter">
                            <a href="{0:s}/{1:02d}/{2:s}">
                                <img src="{0:s}/{1:02d}/{2:s}" alt="No image for beam {1:02d}", width="100%">
                            </a>
                            <div class="w3-container"><h5>Beam {1:02d}</h5></div>
                        </div>\n""".format(page_type, beam_counter, os.path.basename(image))

                if img_counter % 4 == 3 or img_counter == len(image_list)-1:
                    html_code += """</div>\n"""

                img_counter += 1

            html_code += """</div>\n"""
        else:
            logger.warning("No images found for selfcal image gallery")
            html_code += """
                <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('{0:s}')">
                {1:s}
                    </button>
                </div>\n""".format("gallery_images", "Selfcal images")
    else:
        logger.warning("No beams found for selfcal image gallery")
        html_code += """
            <div class="w3-container">
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('{0:s}')">
            {1:s}
                </button>
            </div>\n""".format("gallery_images", "Selfcal images")

    # Gallery of selfcal resdiuals
    # ============================

    # get beams
    beam_dir_list = glob.glob(
        "{0:s}/{1:s}/[0-3][0-9]".format(qa_report_obs_path, page_type))

    n_beams = 40

    image_list = ["" for k in range(2 * n_beams)]

    if len(beam_dir_list) != 0:

        beam_dir_list.sort()

        # go through the beams to get the image directory
        for k in range(len(beam_dir_list)):

            beam_dir = beam_dir_list[k]

            # get the beam which serves as the index for the image list
            beam = int(os.path.basename(beam_dir))

            # get amplitude selfcal residual
            image_list_amp = glob.glob(
                "{0:s}/amplitude*residual.png".format(beam_dir))
            image_list_amp.sort()

            # get phase selfcal residual
            image_list_phase = glob.glob(
                "{0:s}/phase*residual.png".format(beam_dir))
            image_list_phase.sort()

            # if there are no phase selfcal residual, then there are no amplitude selfcal residual
            if len(image_list_phase) != 0:

                # the first image is always from selfcal
                image_first = image_list_phase[0]

                # final selfcal image can be from amplitude selfcal
                if len(image_list_amp) != 0:
                    image_last = image_list_amp[-1]
                else:
                    image_last = image_list_phase[-1]

                # the first image has an even index
                image_list[2 * beam] = image_first
                # the laste image has an uneven index
                image_list[2 * beam + 1] = image_last

        # check that the list of images is not empty
        if len(np.unique(image_list)) != 1:

            html_code += """
                <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('{0:s}')">{1:s}
                    </button>
                </div>
                <div class="w3-container w3-margin-top w3-hide" name="{0:s}">\n""".format("gallery_residuals", "Selfcal residuals")

            img_counter = 0

            beam_counter = 0

            for k in range(len(image_list)):

                # count one beam every second image
                if k != 0 and k % 2 == 0:
                    beam_counter += 1

                image = image_list[k]

                if img_counter % 4 == 0:
                    html_code += """<div class="w3-row">\n"""

                html_code += """
                        <div class="w3-quarter">
                            <a href="{0:s}/{1:02d}/{2:s}">
                                <img src="{0:s}/{1:02d}/{2:s}" alt="No image for beam {1:02d}", width="100%">
                            </a>
                            <div class="w3-container"><h5>Beam {1:02d}</h5></div>
                        </div>\n""".format(page_type, beam_counter, os.path.basename(image))

                if img_counter % 4 == 3 or img_counter == len(image_list)-1:
                    html_code += """</div>\n"""

                img_counter += 1

            html_code += """</div>\n"""
        else:
            logger.warning("No images found for selfcal residual gallery")
            html_code += """
                <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('{0:s}')">
                {1:s}
                    </button>
                </div>\n""".format("gallery_residuals", "Selfcal residuals")
    else:
        logger.warning("No beams found for selfcal residual gallery")
        html_code += """
            <div class="w3-container">
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('{0:s}')">
            {1:s}
                </button>
            </div>\n""".format("gallery_residuals", "Selfcal residual")

    # Selfcal iteration maps sorted by beam
    # =====================================

    # get beams
    beam_list = glob.glob(
        "{0:s}/{1:s}/[0-3][0-9]".format(qa_report_obs_path, page_type))

    n_beams = len(beam_list)

    if n_beams != 0:

        beam_list.sort()

        for k in range(n_beams):

            button_html_name = "beam{0:d}".format(k)
            div_name = "gallery{0:d}".format(k)

            # get the diagnostic plots
            image_list_phase = glob.glob(
                "{0:s}/phase*png".format(beam_list[k]))
            image_list_amp = glob.glob(
                "{0:s}/amplitude*png".format(beam_list[k]))

            n_images = len(image_list_phase) + len(image_list_amp)

            if n_images != 0:

                image_list_phase.sort()
                image_list_amp.sort()

                image_list = np.append(image_list_phase, image_list_amp)

                html_code += """
                    <div class="w3-container">
                        <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('{0:s}')">
                        Beam {1:s}
                        </button>
                    </div>
                    <div class="w3-container w3-margin-top w3-hide" name="{0:s}">\n""".format(div_name, os.path.basename(beam_list[k]))

                img_counter = 0

                for image in image_list:

                    selfcal_type = os.path.basename(image).split("_")[0]

                    major_cycle = os.path.basename(image).split("_")[1]

                    minor_cycle = os.path.basename(image).split("_")[2]

                    image_type = os.path.basename(image).split(".")[
                        0].split("_")[-1]

                    if image_type == "image":
                        caption = "{0:s} image: major {1:s}, minor {2:s}".format(
                            selfcal_type, major_cycle, minor_cycle)
                    elif image_type == "residual":
                        caption = "{0:s} residual: major {1:s}, minor {2:s}".format(
                            selfcal_type, major_cycle, minor_cycle)
                    else:
                        caption = ""

                    if img_counter % 4 == 0:
                        html_code += """<div class="w3-row">\n"""

                    html_code += """
                        <div class="w3-quarter">
                            <a href="{0:s}/{1:s}/{2:s}">
                                <img src="{0:s}/{1:s}/{2:s}" alt="No image", width="100%">
                            </a>
                            <div class="w3-container"><h5>{3:s}</h5></div>
                        </div>\n""".format(page_type, os.path.basename(beam_list[k]), os.path.basename(image), caption)

                    if img_counter % 4 == 3 or img_counter == n_images-1:
                        html_code += """</div>\n"""

                    img_counter += 1

                html_code += """</div>\n"""

                # # go throught the different types of plots
                # # they require a different layout because the plot sizes vary
                # html_code += """<div class="gallery_column" name="{0:s}">\n""".format(
                # div_name)
                # for m in range(n_images):
                #     if m % 4 == 0:
                #         html_code += """<div class="gallery_row">"""

                #     html_code += """<div class="mosaic_img">
                #             <a href="{0:s}/{1:s}/{2:s}">
                #                 <img src="{0:s}/{1:s}/{2:s}" alt="No image", width="100%">
                #             </a>
                #         </div>\n""".format(page_type, os.path.basename(beam_list[k]), os.path.basename(image_list[m]))

                #     if m % 2 != 0 or m == n_images-1:
                #         html_code += """</div>\n"""

            else:
                logger.warning("No selfcal maps found in {0:s}".format(
                    os.path.basename(beam_list[k])))
                html_code += """
                <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" class="disabled" onclick="show_hide_plots('{0:s}')">
                        Beam {1:s}
                    </button>
                </div>\n""".format(button_html_name, os.path.basename(beam_list[k]))

    else:
        logger.warning("No beams for selfcal QA found")
        html_code += """
        <div class="w3-container w3-large w3-text-red">
            <p>
                No beams were found for selfcal QA.
            </p>
        </div>\n"""

    # html_code += """
    #     <p class="info">
    #         The overview does not cover selfcal QA yet
    #     </p>\n
    #     """

    return html_code
