#!/usr/bin/python2.7

"""
This file contains functionality to create the content for the
each subpage of the report
"""
import os
import sys
from astropy.table import Table
import logging
import glob
import time
import socket


def write_obs_content(page_name, qa_report_path, page_type='', obs_id=0):
    """
    Function to write Observation content
    """

    # empty string of html code to start with
    html_code = """"""

    #html_code = """<p>NOTE: When clicking on the buttons for the first time, please click twice (small bug)</p>"""

    # create html content for subpage prepare
    # +++++++++++++++++++++++++++++++++++++++
    if page_type == 'prepare':

        # get beams
        if obs_id != 0:
            beam_list = glob.glob(
                "{0:s}/{1:d}/{2:s}/[0-3][0-9]".format(qa_report_path, obs_id, page_type))
        else:
            beam_list = glob.glob(
                "{0:s}/{1:s}/[0-3][0-9]".format(qa_report_path, page_type))

        n_beams = len(beam_list)

        if n_beams != 0:

            beam_list.sort()

            for k in range(n_beams):

                # get the images
                images_in_beam = glob.glob("{0:s}/*png".format(beam_list[k]))

                if len(images_in_beam) != 0:

                    images_in_beam.sort()

                    div_name = "gallery{0:d}".format(k)

                    html_code += """<button onclick="show_hide_plots('{0:s}')">
                            Beam {1:s}
                        </button>\n""".format(div_name, os.path.basename(beam_list[k]))

                    for image in images_in_beam:
                        html_code += """<div class="gallery" name="{0:s}">
                                <a href="{1:s}/{2:s}/{3:s}">
                                    <img src="{1:s}/{2:s}/{3:s}" alt="No image", width="100%">
                                </a>
                                <div class="caption">{3:s}</div>
                            </div>\n""".format(div_name, page_type, os.path.basename(beam_list[k]), os.path.basename(image))
                    html_code += """\n"""
                else:
                    print("ERROR: No images in beam {0:s} found".format(
                        beam_list[k]))
        else:
            print("ERROR: No beams found for prepare found")
            return -1

    # create html content for subpage crosscal
    # ++++++++++++++++++++++++++++++++++++++++
    elif page_type == 'crosscal':

        # the different plots
        categories = ["BP_amp", "BP_phase", "Corrected_amp", "Corrected_phase",
                      "Gain_amp", "Gain_phase", "Model_amp", "Model_phase", "Raw_amp", "Raw_phase"]

        categories_titles = ["Bandpass Amplitude", "Bandpass Phase", "Corrected Amplitude", "Corrected Phase",
                             "Gain factors Amplitude", "Gain factors Phase", "Model Amplitude", "Model Phase", "Raw visibility Amplitude", "Raw Visibility Phase"]

        n_cats = len(categories)

        # get the images
        if obs_id != 0:
            image_list = glob.glob(
                "{0:s}/{1:d}/{2:s}/*png".format(qa_report_path, obs_id, page_type))
        else:
            image_list = glob.glob(
                "{0:s}/{1:s}/*png".format(qa_report_path, page_type))

        if len(image_list) != 0:
            # go throught the different types of plots
            for k in range(n_cats):

                # get list of plots for this category
                cat_plots = [pl for pl in image_list if categories[k] in pl]

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

                    div_name = "gallery{0:d}".format(k)

                    html_code += """<button onclick="show_hide_plots('{0:s}')">
                            {1:s}
                        </button>\n""".format(div_name, categories_titles[k])

                    for image in cat_plots:
                        html_code += """<div class="gallery" name="{0:s}">
                                <a href="{1:s}/{2:s}">
                                    <img src="{1:s}/{2:s}" alt="No image", width="100%">
                                </a>
                            </div>\n""".format(div_name, page_type, os.path.basename(image))
                    html_code += """\n"""
        else:
            print("ERROR: No crosscal plots found")
            return -1

    # create html content for subpage prepare
    # +++++++++++++++++++++++++++++++++++++++
    elif page_type == "apercal_log":

        # get the log files in linke to the apercal_log report directory:
        log_file_list = glob.glob(
            "{0:s}/{1:d}/apercal_log/apercal_beam*.log".format(qa_report_path, obs_id))

        n_log_files = len(log_file_list)

        if n_log_files != 0:

            log_file_list.sort()

            # go through the log files and create iframes
            for k in range(n_log_files):

                frame_name = "logfile{0:d}".format(k)

                log_file_beams = os.path.basename(
                    log_file_list[k]).split("_")[-1].replace(".log", "")

                button_name = "Apercal logfile for Beams {0:s}".format(
                    log_file_beams)

                html_code += """<button onclick="show_hide_plots('{0:s}')">
                            {1:s}
                        </button>\n""".format(frame_name, button_name)

                html_code += """<p>
                        <iframe id="log" name="{0:s}" src="{1:s}/{2:s}"></iframe>
                    </p>\n""".format(frame_name, page_type, os.path.basename(log_file_list[k]))

        else:
            print("ERROR: No apercal log files found")
            return -1

    try:
        html_file = open(page_name, 'a')
        html_file.write(html_code)
        html_file.close()
    except Exception as e:
        logging.error(e)
        print("ERROR writing obs content")
        return -1

    return 1
