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

logger = logging.getLogger(__name__)


def write_obs_content_preflag(html_code, qa_report_obs_path, page_type):
    """Function to create the html page for preflag
    """

    logger.info("Writing html code for page {0:s}".format(page_type))

    html_code += """
        <p class="info">
            Here you can go through the different plots created by preflag.
        </p>\n
        """

    # get beams
    beam_list = glob.glob(
        "{0:s}/{1:s}/[0-3][0-9]".format(qa_report_obs_path, page_type))

    n_beams = len(beam_list)

    if n_beams != 0:

        beam_list.sort()

        for k in range(n_beams):

            # get the images
            images_in_beam = glob.glob("{0:s}/*png".format(beam_list[k]))

            if len(images_in_beam) != 0:

                images_in_beam.sort()

                div_name = "gallery{0:d}".format(k)

                html_code += """
                    <button onclick="show_hide_plots('{0:s}')">
                        Beam {1:s}
                    </button>\n""".format(div_name, os.path.basename(beam_list[k]))

                for image in images_in_beam:
                    html_code += """
                        <div class="gallery" name="{0:s}">
                            <a href="{1:s}/{2:s}/{3:s}">
                                <img src="{1:s}/{2:s}/{3:s}" alt="No image", width="100%">
                            </a>
                            <div class="caption">{3:s}</div>
                        </div>\n""".format(div_name, page_type, os.path.basename(beam_list[k]), os.path.basename(image))
                html_code += """\n"""
            else:
                logger.warning("No images in beam {0:s} found".format(
                    beam_list[k]))

                html_code += """
                <button onclick="show_hide_plots('{0:s}')">
                        Beam {1:s}
                    </button>\n""".format(div_name, os.path.basename(beam_list[k]))

                html_code += """
                    <div class="gallery" name="{0:s}">
                        <p class="warning">
                            No plots were found for {1:s}
                        </p>
                    </div>\n""".format(div_name, page_type)
    else:
        logger.warning("No beams found for preflag found")
        html_code += """
        <p class="warning">
            No plots were found for preflag
        </p>\n"""

    return html_code


def write_obs_content_crosscal(html_code, qa_report_obs_path, page_type):
    """Function to create the html page for crosscal
    """

    logger.info("Writing html code for page {0:s}".format(page_type))

    html_code += """
        <p class="info">
            Here you can go through the different plots created by crosscal.
        </p>\n
        """
    # the different plots
    categories = ["BP_amp", "BP_phase", "Corrected_amp", "Corrected_phase",
                  "Gain_amp", "Gain_phase", "Model_amp", "Model_phase", "Raw_amp", "Raw_phase"]

    categories_titles = ["Bandpass Amplitude", "Bandpass Phase", "Corrected Amplitude", "Corrected Phase",
                         "Gain factors Amplitude", "Gain factors Phase", "Model Amplitude", "Model Phase", "Raw visibility Amplitude", "Raw Visibility Phase"]

    n_cats = len(categories)

    # get the images
    image_list = glob.glob(
        "{0:s}/{1:s}/*png".format(qa_report_obs_path, page_type))

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
                    html_code += """
                        <div class="gallery" name="{0:s}">
                            <a href="{1:s}/{2:s}">
                                <img src="{1:s}/{2:s}" alt="No image", width="100%">
                            </a>
                        </div>\n""".format(div_name, page_type, os.path.basename(image))
                html_code += """\n"""
            else:

                div_name = "gallery{0:d}".format(k)

                html_code += """
                    <button onclick="show_hide_plots('{0:s}')">
                        {1:s}
                    </button>\n""".format(div_name, categories_titles[k])

                html_code += """
                    <div class="gallery" name="{0:s}">
                        <p class="warning">
                            No plots were found for {1:s}
                        </p>
                    </div>\n""".format(div_name, categories_titles[k])

    else:
        logger.warning("No crosscal plots found")
        html_code += """
        <p class="warning">
            No plots were found for crosscal
        </p>\n"""

    return html_code


def write_obs_content_apercal_log(html_code, qa_report_obs_path, page_type):
    """Function to create the html page for apercal_log
    """

    logger.info("Writing html code for page {0:s}".format(page_type))

    html_code += """
        <p class="info">
            Here you can go through the four log files created by apercal.
        </p>\n
        """

    # get the log files in linke to the apercal_log report directory:
    log_file_list = glob.glob(
        "{0:s}/{1:s}/apercal_log_happili*.txt".format(qa_report_obs_path, page_type))

    n_log_files = len(log_file_list)

    if n_log_files != 0:

        log_file_list.sort()

        # go through the log files and create iframes
        for k in range(n_log_files):

            # create content for iframe
            frame_name = "logfile{0:d}".format(k)

            log_file_happili = os.path.basename(
                log_file_list[k]).split("_")[-1].replace("txt", "")

            button_name = "Apercal logfile for {0:s}".format(
                log_file_happili)

            html_code += """<button onclick="show_hide_plots('{0:s}')">
                        {1:s}
                    </button>\n""".format(frame_name, button_name)

            html_code += """<p>
                    <iframe id="log" name="{0:s}" src="{1:s}/{2:s}"></iframe>
                </p>\n""".format(frame_name, page_type, os.path.basename(log_file_list[k]).replace(".txt", ".html"))

            # create iframe supbage
            html_code_iframe_page = """<!DOCTYPE HTML>
                <html lang="en">

                <head>
                <meta http-equiv="content-type" content="text/html; charset=utf-8" />
                <meta name="description" content="" />
                <meta name="keywords" content="" />
                </head>

                <body>
                <a href="{0:s}" target="_self">Click here to open log file</a>
                </body>

                </html>\n""".format(os.path.basename(log_file_list[k]))

            iframe_page_name = "{0:s}/{1:s}/{2:s}".format(qa_report_obs_path, page_type, os.path.basename(
                log_file_list[k]).replace(".txt", ".html"))
            try:
                logger.info(
                    "Writing apercal log iframe page {0:s}".format(iframe_page_name))
                html_file = open(iframe_page_name, 'w')
                html_file.write(html_code_iframe_page)
                html_file.close()
            except Exception as e:
                logger.error(e)
                logger.error("writing iframe page content failed")
    else:
        logger.warning("No apercal log files found in {0:s}/{1:s}/".format(
            qa_report_obs_path, page_type))

    return html_code


def write_obs_content(page_name, qa_report_path, page_type='', obs_id=''):
    """
    Function to write Observation content
    """

    # empty string of html code to start with
    html_code = """"""

    # html_code = """<p>NOTE: When clicking on the buttons for the first time, please click twice (small bug)</p>"""

    qa_report_obs_path = "{0:s}/{1:s}".format(qa_report_path, obs_id)

    # create html content for subpage preflag
    # +++++++++++++++++++++++++++++++++++++++
    if page_type == 'preflag':

        try:
            html_code = write_obs_content_preflag(
                html_code, qa_report_obs_path, page_type)
        except Exception as e:
            logger.error(e)

    # create html content for subpage crosscal
    # ++++++++++++++++++++++++++++++++++++++++
    elif page_type == 'crosscal':

        try:
            html_code = write_obs_content_crosscal(
                html_code, qa_report_obs_path, page_type)
        except Exception as e:
            logger.error(e)

    # create html content for subpage continuum
    # +++++++++++++++++++++++++++++++++++++++++
    elif page_type == 'continuum':

        # get beams
        if obs_id != 0:
            beam_list = glob.glob(
                "{0:s}/{1:s}/{2:s}/[0-3][0-9]".format(qa_report_path, obs_id, page_type))
        else:
            beam_list = glob.glob(
                "{0:s}/{1:s}/[0-3][0-9]".format(qa_report_path, page_type))

        n_beams = len(beam_list)

        if n_beams != 0:

            beam_list.sort()

            for k in range(n_beams):

                # get the diagnostic plots
                image_list = glob.glob("{0:s}/*png".format(beam_list[k]))

                n_images = len(image_list)

                if n_images != 0:

                    image_list.sort()

                    button_html_name = "beam{0:d}".format(k)
                    div_name = "continuum_gallery{0:d}".format(k)

                    html_code += """<button onclick="show_hide_plots('{0:s}')">
                                Beam {1:s}
                            </button>
                            <div class="beam_continuum" name="{0:s}">
                                <button class="button_continuum" onclick="show_hide_plots('{2:s}')">
                                    PyBDSF Diagnostic plots
                                </button>
                            \n""".format(button_html_name, os.path.basename(beam_list[k]), div_name)

                    html_code += """<div class="gallery_row" name="{0:s}">\n""".format(
                        div_name)

                    # go throught the different types of plots
                    # they require a different layout because the plot sizes vary
                    for m in range(n_images):
                        if m % 2 == 0:
                            html_code += """<div class="gallery_column">"""

                        html_code += """<div class="mosaic_img">
                                <a href="{0:s}/{1:s}/{2:s}">
                                    <img src="{0:s}/{1:s}/{2:s}" alt="No image", width="100%">
                                </a>
                            </div>\n""".format(page_type, os.path.basename(beam_list[k]), os.path.basename(image_list[m]))

                        if m % 2 != 0 or m == n_images-1:
                            html_code += """</div>\n"""

                    html_code += """</div>\n"""
                else:
                    logger.error("No mosaic plots found")

                # add the validation tool
                frame_name = "validation_tool"

                button_name = "Validation tool"

                html_code += """<button class="button_continuum" onclick="show_hide_plots('{0:s}')">
                            {1:s}
                        </button>\n""".format(frame_name, button_name)

                html_code += """<p>
                        <iframe id="validation_tool" name="{0:s}" src="{1:s}/{2:s}/{3:s}/index.html"></iframe>
                    </p>
                    </div>\n""".format(frame_name, page_type, os.path.basename(beam_list[k]), "validation_tool")
        else:
            logger.error("No beams for continuum QA found")
            return -1

    # create html content for subpage mosaic
    # ++++++++++++++++++++++++++++++++++++++
    elif page_type == 'mosaic':

        # get the diagnostic plots
        if obs_id != 0:
            image_list = glob.glob(
                "{0:s}/{1:s}/{2:s}/*png".format(qa_report_path, obs_id, page_type))
        else:
            image_list = glob.glob(
                "{0:s}/{1:s}/*png".format(qa_report_path, page_type))

        n_images = len(image_list)

        if n_images != 0:

            div_name = "mosaic_gallery"

            html_code += """<button onclick="show_hide_plots('{0:s}')">
                        PyBDSF Diagnostic plots
                    </button>
                    <div class="gallery_row" , name="mosaic_gallery">\n""".format(div_name)

            # go throught the different types of plots
            # they require a different layout because the plot sizes vary
            for k in range(n_images):
                if k % 2 == 0:
                    html_code += """<div class="gallery_column">"""

                html_code += """<div class="mosaic_img">
                        <a href="{0:s}/{1:s}">
                            <img src="{0:s}/{1:s}" alt="No image", width="100%">
                        </a>
                    </div>\n""".format(page_type, os.path.basename(image_list[k]))

                if k % 2 != 0 or k == n_images-1:
                    html_code += """</div>\n"""

            html_code += """</div>\n"""
        else:
            logger.error("No mosaic plots found")
            return -1

        # add the validation tool
        frame_name = "validation_tool"

        button_name = "Validation tool for mosaic"

        html_code += """<button onclick="show_hide_plots('{0:s}')">
                            {1:s}
                        </button>\n""".format(frame_name, button_name)

        html_code += """<p>
                        <iframe id="validation_tool" name="{0:s}" src="{1:s}/{2:s}/index.html"></iframe>
                    </p>\n""".format(frame_name, page_type, "validation_tool")

    # create html content for subpage apercal
    # as this is a text file, it is a bit more
    # complicated and requires creating a dummy
    # html file. Otherwise, it can automatically
    # trigger the download questions
    # +++++++++++++++++++++++++++++++++++++++
    elif page_type == "apercal_log":

        try:
            html_code = write_obs_content_apercal_log(
                html_code, qa_report_obs_path, page_type)
        except Exception as e:
            logger.error(e)

    try:
        html_file = open(page_name, 'a')
        html_file.write(html_code)
        html_file.close()
    except Exception as e:
        logger.error(e)
        logger.error("writing obs content")
        return -1

    return 1
