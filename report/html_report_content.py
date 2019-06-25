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

def write_obs_content_summary(html_code, qa_report_obs_path, page_type):
    """Function to create the html page for summary

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
            <p>Here you will find a summary plot with compound beams.</p>
        </div>\n
        """

    # Create html code for inspection plots
    # =====================================
    # get images
    image_list = glob.glob(
        "{0:s}/{1:s}/*.png".format(qa_report_obs_path, page_type))

    if len(image_list) != 0:
        html_code += """
                <div class="w3-container w3-margin-top w3-show">\n"""

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

def write_obs_content_preflag(html_code, qa_report_obs_path, page_type):
    """Function to create the html page for preflag
    """

    logger.info("Writing html code for page {0:s}".format(page_type))

    html_code += """
        <div class="w3-container w3-large">
            <p>Here you can go through the different plots created by preflag.</p>
        </div>\n
        """

    # Create html code for summary table
    # ==================================
    
    table_found = True

    if table_found:
        html_code += """
            <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('gallery-2')">
                        Preflag summary table
                    </button>
                </div>
            <div class="w3-container w3-margin-top w3-show" name="gallery-2">\n"""

        html_code += """
            <p> No table here yet.
            </p>\n"""
        html_code += """</div>\n"""
    else:
        logger.warning("No combined preflag plots found")
        html_code += """
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('gallery-2')">
                    Preflag summary table
                </button>\n"""

    # Create html code for combined preflag plots
    # ===========================================
    # get images
    image_list = glob.glob(
        "{0:s}/{1:s}/*.png".format(qa_report_obs_path, page_type))
    
    if len(image_list) != 0:
        html_code += """
                <div class="w3-container">
                        <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('gallery-1')">
                            Combined plots
                        </button>
                    </div>
                <div class="w3-container w3-margin-top w3-hide" name="gallery-1">\n"""
        
        img_counter = 0

        for image in image_list:
            if img_counter % 3 == 0:
                html_code += """<div class="w3-row">\n"""

            html_code += """
                <div class="w3-third">
                    <a href="{0:s}/{1:s}">
                        <img src="{0:s}/{1:s}" alt="No image" style="width:100%">
                    </a>
                    <!-- <div class="w3-container w3-center">
                        <h5>{1:s}</h5>
                    </div> --!>
                </div>\n""".format(page_type, os.path.basename(image))
            
            if img_counter % 3 == 2 or img_counter == len(image_list)-1:
                html_code += """</div>\n"""

            img_counter += 1

        html_code += """</div>\n"""
    else:
        logger.warning("No combined preflag plots found")
        html_code += """
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('gallery-1')">
                    Combined plots
                </button>\n"""


    # Create html code for individual beam plots
    # ==========================================

    # get beams
    beam_list = glob.glob(
        "{0:s}/{1:s}/[0-3][0-9]".format(qa_report_obs_path, page_type))

    n_beams = len(beam_list)

    # if there are beams go through them
    if n_beams != 0:

        beam_list.sort()

        for k in range(n_beams):

            # get the images
            images_in_beam = glob.glob("{0:s}/*png".format(beam_list[k]))

            div_name = "gallery{0:d}".format(k)

            if len(images_in_beam) != 0:

                images_in_beam.sort()

                html_code += """
                    <div class="w3-container">
                        <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('{0:s}')">
                            Beam {1:s}
                        </button>
                    </div>
                    <div class="w3-container w3-margin-top w3-hide" name="{0:s}">\n""".format(div_name, os.path.basename(beam_list[k]))

                img_counter = 0

                for image in images_in_beam:
                    if img_counter % 3 == 0:
                        html_code += """<div class="w3-row">\n"""

                    html_code += """
                        <div class="w3-third">
                            <a href="{0:s}/{1:s}/{2:s}">
                                <img src="{0:s}/{1:s}/{2:s}" alt="No image" style="width:100%">
                            </a>
                            <div class="w3-container w3-center">
                                <h5>{2:s}</h5>
                            </div>
                        </div>\n""".format(page_type, os.path.basename(beam_list[k]), os.path.basename(image))
                    
                    if img_counter % 3 == 2 or img_counter == len(images_in_beam)-1:
                        html_code += """</div>\n"""
                    
                    img_counter += 1

                html_code += """</div>\n"""
            else:
                logger.warning("No images in beam {0:s} found".format(
                    beam_list[k]))

                html_code += """
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('{0:s}')">
                        Beam {1:s}
                    </button>\n""".format(div_name, os.path.basename(beam_list[k]))

                # html_code += """
                #     <div class="gallery" name="{0:s}">
                #         <p class="warning">
                #             No plots were found for {1:s}
                #         </p>
                #     </div>\n""".format(div_name, page_type)
    else:
        logger.warning("No beams found for preflag found")
        html_code += """
        <div class="w3-container w3-large w3-text-red">
            <p>
                No plots were found for preflag
            </p>
        </div>\n"""

    return html_code


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
    categories = ["BP_amp", "BP_phase", "Gain_amp", "Gain_phase", "K_", "Df_amp", "Df_phase", "Kcross", "Xf_amp", "Xf_phase", "Raw_amp", "Raw_phase", "Model_amp", "Model_phase", "Corrected_amp", "Corrected_phase"]

    categories_titles = ["Bandpass Amplitude", "Bandpass Phase", "Gain factors Amplitude", "Gain factors Phase", "Global Delay", "Leakage Amplitude", "Leakage Phase", "Cross Hand Delay", "Polarization Angle Amplitude", "Polarization Angle Phase", "Raw visibility Amplitude", "Raw Visibility Phase", "Model Amplitude", "Model Phase", "Corrected Amplitude", "Corrected Phase"]

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


def write_obs_content_selfcal(html_code, qa_report_obs_path, page_type):
    """Function to create the html page for selfcal

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
                This page shows the images and residuals from every major and minor phase self-cal iteration.
                In addition selfcal phase and amplitude gains are shown for each antenna. <br>
                This page will only have content after the selfcal QA step has been performed.
            </p>
        </div>\n
        """

    # Create html code for summary table
    # ==================================

    table_found = False

    if table_found:
        html_code += """
            <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('gallery-1')">
                        Selfcal summary table
                    </button>
                </div>
            <div class="w3-container w3-margin-top w3-show" name="gallery-1">\n"""

        html_code += """
            <p> No table here yet.
            </p>\n"""
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
    phase_list = glob.glob("{0:s}/{1:s}/SCAL_phase*png".format(qa_report_obs_path, page_type))

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

            if img_counter % 3 == 2:
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
    amp_list = glob.glob("{0:s}/{1:s}/SCAL_amp*png".format(qa_report_obs_path, page_type))

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
                <div class="third">
                    <a href="{0:s}/{1:s}">
                    <img src="{0:s}/{1:s}" alt="No image", width="100%">
                    </a>
                </div>\n""".format(page_type, os.path.basename(image))

            if img_counter % 3 == 2:
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
            image_list = glob.glob("{0:s}/*png".format(beam_list[k]))

            n_images = len(image_list)

            if n_images != 0:

                image_list.sort()

                html_code += """
                    <div class="w3-container">
                        <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('{0:s}')">
                        Beam {1:s}
                        </button>
                    </div>
                    <div class="w3-container w3-margin-top w3-hide" name="{0:s}">\n""".format(div_name, os.path.basename(beam_list[k]))

                img_counter = 0

                for image in image_list:

                    major_cycle = os.path.basename(image).split("_")[0]

                    minor_cycle = os.path.basename(image).split("_")[1]

                    image_type = os.path.basename(image).split(".")[
                        0].split("_")[-1]
                    
                    if image_type == "image":
                        caption = "Image: major {0:s}, minor {1:s}".format(major_cycle, minor_cycle)
                    elif image_type == "residual":
                        caption = "Residual: major {0:s}, minor {1:s}".format(
                            major_cycle, minor_cycle)
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


def write_obs_content_continuum(html_code, qa_report_obs_path, page_type):
    """Function to create the html page for continuum

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
                Here you can inspect for each beam the continuum image, PyBDSF diagnostic plots and the validation tool. The PyBDSF catalog is not accessible from this page, but can be found in the QA directory as a csv table.
                Of course, all of this only exists for beams with a continuum image created by the pipeline.<br>
                This page will only have content after the continuum QA step has been performed.
            </p>
        </div>\n
        """

    # Create html code for summary table
    # ==================================

    table_found = False

    if table_found:
        html_code += """
            <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('gallery-1')">
                        Continuum summary table
                    </button>
                </div>
            <div class="w3-container w3-margin-top w3-show" name="gallery-1">\n"""

        html_code += """
            <p> No table here yet.
            </p>\n"""
        html_code += """</div>\n"""
    else:
        logger.warning("No continuum table found")
        html_code += """
            <div class="w3-container">
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('gallery-1')">
                    Continuum summary table
                </button>
            </div>\n"""

    # Create html code for continuum images gallery
    # =============================================

    # get the phase plots
    image_list = glob.glob(
        "{0:s}/{1:s}/[0-3][0-9]/image_mf_[0-9][0-9].png".format(qa_report_obs_path, page_type))

    if len(image_list) != 0:
        html_code += """
            <div class="w3-container">
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('{0:s}')">{1:s}
                </button>
            </div>
            <div class="w3-container w3-margin-top w3-hide" name="{0:s}">\n""".format("gallery_cont", "Continuum images")

        img_counter = 0

        for image in image_list:

            if img_counter % 3 == 0:
                html_code += """<div class="w3-row">\n"""

            html_code += """
            <div class="w3-third">
                <a href="{0:s}/{1:s}/{2:s}">
                <img src="{0:s}/{1:s}/{2:s}" alt="No image", width="100%">
                </a>
                <div class="w3-container w3-center">
                    <h5>Beam {1:s}</h5>
                </div>
            </div>\n""".format(page_type, os.path.basename(os.path.dirname(image)), os.path.basename(image))

            if img_counter % 3 == 2:
                html_code += """</div>\n"""

            img_counter += 1

        html_code += """</div>\n"""
    else:
        html_code += """
            <div class="w3-container">
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('{0:s}')">
            {1:s}
                </button>
            </div>\n""".format("gallery_cont", "Continuum images")


    # Create html code for beam plots
    # ===============================


    # get beams
    beam_list = glob.glob(
        "{0:s}/{1:s}/[0-3][0-9]".format(qa_report_obs_path, page_type))

    n_beams = len(beam_list)

    if n_beams != 0:

        beam_list.sort()

        for k in range(n_beams):

            button_html_name = "beam{0:d}".format(k)
            div_name = "continuum_gallery{0:d}".format(k)

            # get the diagnostic plots
            image_list = glob.glob("{0:s}/*png".format(beam_list[k]))

            n_images = len(image_list)

            if n_images != 0:

                image_list.sort()

                html_code += """
                        <div class="w3-container">
                            <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('{0:s}')">
                            Beam {1:s}
                            </button>
                        </div>
                        <div class="w3-container w3-margin-top w3-hide" name="{0:s}">
                            <div class="w3-container">
                                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-dark-gray w3-hover-gray w3-margin-bottom" class="button_continuum" onclick="show_hide_plots('{2:s}')">
                                    PyBDSF Diagnostic plots
                                </button>
                            </div>
                            <div class="w3-container w3-margin-top w3-hide" name="{2:s}">\n""".format(button_html_name, os.path.basename(beam_list[k]), div_name)

                # go throught the different types of plots
                # they require a different layout because the plot sizes vary
                for m in range(n_images):

                    if m % 3 == 0:
                        html_code += """<div class="w3-row">\n"""
                    
                    html_code += """
                        <div class="w3-third">
                            <a href="{0:s}/{1:s}/{2:s}">
                                <img src="{0:s}/{1:s}/{2:s}" alt="No image", width="100%">
                            </a>
                        </div>\n""".format(page_type, os.path.basename(beam_list[k]), os.path.basename(image_list[m]))

                    if m % 3 == 2 or m == n_images-1:
                        html_code += """</div>\n"""

                html_code += """</div>\n"""

                # add the validation tool
                frame_name = glob.glob(
                    "{0:s}/*continuum_validation_pybdsf_snr5.0_int".format(beam_list[k]))

                if len(frame_name) != 0 and len(frame_name) == 1:
                    frame_name = frame_name[0]

                    if os.path.isdir(frame_name):

                        button_name = "validation_tool{0:d}".format(k)

                        html_code += """
                            <div class="w3-container">
                                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-dark-gray w3-hover-gray w3-margin-bottom" class="button_continuum" onclick="show_hide_plots('{0:s}')">
                                    Validation Tool
                                </button>
                            </div>
                            <div class="w3-container w3-margin-top w3-hide" name="{0:s}">\n""".format(button_name)

                        html_code += """
                                <div class="w3-container w3-large">
                                    <a href="{0:s}/{1:s}/{2:s}/index.html">Click here to open the validation tool</a> if it is not shown below
                                </div>
                                <div class="w3-container">
                                    <iframe class="w3-container" style="width:100%; height:1200px" src="{0:s}/{1:s}/{2:s}/index.html"></iframe>
                                </div>
                            </div>\n""".format(page_type, os.path.basename(beam_list[k]), os.path.basename(frame_name))
                    else:
                        logger.warning("No continuum validation tool found for beam {0:s}".format(
                            os.path.basename(beam_list[k])))
                        html_code += """
                            <div class="w3-container w3-margin-top w3-hide" name="{0:s}">
                                <p class="warning">
                                    No plots and validation tool were found for {1:s}
                                </p>
                            </div>\n""".format(button_html_name, page_type)
                else:
                    logger.warning("No continuum validation tool found for beam {0:s}".format(
                        os.path.basename(beam_list[k])))
                    html_code += """
                        <div class="w3-container w3-large w3-text-red" name="{0:s}">
                            <p>
                                No plots and validation tool were found for {1:s}
                            </p>
                        </div>\n""".format(button_html_name, page_type)

            else:
                logger.warning("No continuum plots and validation found for beam {0:s}".format(
                    os.path.basename(beam_list[k])))
                html_code += """
                <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" class="disabled" onclick="show_hide_plots('{0:s}')">
                        Beam {1:s}
                    </button>
                </div>\n""".format(button_html_name, os.path.basename(beam_list[k]))

            html_code += """</div>\n"""

                # html_code += """
                #     <div class="gallery" name="{0:s}">
                #         <p class="warning">
                #             No plots and validation tool were found for {1:s}
                #         </p>
                #     </div>\n""".format(button_html_name, page_type)

    else:
        logger.warning("No beams for continuum QA found")
        html_code += """
        <div class="w3-container w3-large w3-text-red">
            <p>
                No beams were found for continuum QA.
            </p>
        </div\n"""

    return html_code


def write_obs_content_line(html_code, qa_report_obs_path, page_type):
    """Function to create the html page for line

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
                Here you can find a plot of the noise versus channel/frequency for all available cubes. 
                Please note that at this stage, the cube is cleaned and continuum subtracted. The rms is determined over the entire
                image without taking into account the existenc of continuum sources. The fit is a simple Gaussian fit to the noise of 
                each channel
                The noise data is not accessible from this page, but can be found in the QA directory as a csv table.<br>
                This page will only have content after the line QA step has been performed.
            </p>
        </div>\n
        """

    # Create html code for summary table
    # ==================================

    table_found = False

    if table_found:
        html_code += """
            <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('gallery-1')">
                        Line summary table
                    </button>
                </div>
            <div class="w3-container w3-margin-top w3-show" name="gallery-1">\n"""

        html_code += """
            <p> No table here yet.
            </p>\n"""
        html_code += """</div>\n"""
    else:
        logger.warning("No line table found")
        html_code += """
            <div class="w3-container">
                <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('gallery-1')">
                    Line summary table
                </button>
            </div>\n"""

    # Create html code for image gallery
    # ==================================

    # get beams
    beam_list = glob.glob(
        "{0:s}/{1:s}/[0-3][0-9]".format(qa_report_obs_path, page_type))

    n_beams = len(beam_list)

    if n_beams != 0:

        beam_list.sort()

        for k in range(n_beams):

            # get the images
            images_in_beam = glob.glob("{0:s}/*png".format(beam_list[k]))

            div_name = "gallery{0:d}".format(k)

            if len(images_in_beam) != 0:

                images_in_beam.sort()

                html_code += """
                    <div class="w3-container">
                        <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('{0:s}')">
                            Beam {1:s}
                        </button>
                    </div>
                    <div class="w3-container w3-margin-top w3-hide" name="{0:s}">\n""".format(div_name, os.path.basename(beam_list[k]))

                img_counter = 0

                for image in images_in_beam:
                    
                    if img_counter % 3 == 0:
                        html_code += """<div class="w3-row">\n"""

                    html_code += """
                        <div class="w3-thrid">
                            <a href="{0:s}/{1:s}/{2:s}">
                                <img src="{0:s}/{1:s}/{2:s}" alt="No cube available for beam {1:s}", width="100%">
                            </a>
                            <div class="w3-container w3-center"><h5>{2:s}</h5></div>
                        </div>\n""".format(page_type, os.path.basename(beam_list[k]), os.path.basename(image))
                    
                    if img_counter % 3 == 2 or img_counter == len(images_in_beam) - 1:
                        html_code += """</div>\n"""

                    img_counter += 1

                html_code += """</div>\n"""
            else:
                logger.warning("No plot for cube in beam {0:s} found".format(
                    beam_list[k]))

                html_code += """
                    <div class="w3-container">
                        <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" onclick="show_hide_plots('{0:s}')">
                            Beam {1:s}
                        </button>
                    </div>\n""".format(div_name, os.path.basename(beam_list[k]))

                # html_code += """
                #     <div class="gallery" name="{0:s}">
                #         <p class="warning">
                #             No plots were found for {1:s}
                #         </p>
                #     </div>\n""".format(div_name, page_type)
    else:
        logger.warning("No beams found for cube found")
        html_code += """
        <div class="w3-container w3-large w3-text-red">
            <p>
                No plots were found for cube
            </p>
        </div>\n"""

    # html_code += """
    #     <p class="info">
    #         The overview does not cover line QA yet
    #     </p>\n0
    #     """

    return html_code


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


def write_obs_content_apercal_log(html_code, qa_report_obs_path, page_type):
    """Function to create the html page for apercal_log

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
                Here you can go through the four log files created by apercal. 
                Click on one of the buttons and then on the link to open the log file. 
                You can use the search function of your browser to search the log files.
            </p>
        </div>\n
        """

    node_list = np.array(
        ["happili-01", "happili-02", "happili-03", "happili-04"])

    for node in node_list:

        # get the log files in linke to the apercal_log report directory:
        log_file_list = glob.glob(
            "{0:s}/{1:s}/apercal*_log_{2:s}.txt".format(qa_report_obs_path, page_type, node))

        # get the log files in linke to the apercal_log report directory:
        csv_file = "{0:s}/{1:s}/apercal_log_timeinfo_{2:s}.csv".format(
            qa_report_obs_path, page_type, node)

        button_name = "Apercal performance on {0:s}".format(node)

        # number of logfiles
        n_log_files = len(log_file_list)

        if n_log_files != 0 or os.path.exists(csv_file):

            # create button
            html_code += """
                <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom" onclick="show_hide_plots('{0:s}')">
                        {1:s}
                    </button>
                </div>
                <div class="w3-container w3-margin-top w3-hide" name = "{0:s}" >\n""".format(node, button_name)

            # create a table with the time info
            # +++++++++++++++++++++++++++++++++
            if os.path.exists(csv_file):

                logger.info(
                    "Creating table with apercal timing information from {0:s}".format(node))

                frame_name = "apercal_gallery_table_{0:s}".format(node)

                html_code += """
                        <div class="w3-container">
                            <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-dark-gray w3-hover-gray w3-margin-bottom" onclick="show_hide_plots('{0:s}')">
                                Apercal timing information
                            </button>
                        </div>
                        <div class="w3-container w3-margin-top w3-margin-bottom w3-hide" name = "{0:s}" >
                        """.format(frame_name)

                # read in data
                timinginfo_table = Table.read(csv_file, format="csv")

                pipeline_step_list = ["start_pipeline", "prepare", "preflag", "ccal", "convert", "scal", "continuum", "line"]

                # # get the minimum and maximum values for each step
                # pipeline_step_max_list = np.array([str for pipeline_step in pipeline_step_list])
                # pipeline_step_min_list = np.array([str for pipeline_step in pipeline_step_list])

                # for k in range(len(pipeline_step_list)):
                #     pipeline_step_max_list[k] = np.max()

                # create the table
                # start with the header
                html_code += """
                        <div class="w3-responsive">
                            <table class="w3-table-all">
                                <tr class="w3-amber">
                                    <th>beam</th>"""
                
                for pipeline_step in pipeline_step_list:
                    html_code += """
                                    <th>{0:s}</th>
                        """.format(pipeline_step)
                html_code += """</tr>
                        """

                # get a list of beams in the file
                timinginfo_beam_list = np.unique(timinginfo_table['beam'])


                # go through elements in list and fill the table
                for timinginfo_beam in timinginfo_beam_list:

                    html_code += """<tr>
                                    <td>{0:s}</td>
                            """.format(timinginfo_beam)

                    # get part of the table for the given beam
                    timinginfo_table_select = timinginfo_table[np.where(timinginfo_table['beam']==timinginfo_beam)]

                    # go through the pipeline steps
                    #table_pipeline_steps = timinginfo_table_select['pipeline_steps']
                    for pipeline_step in pipeline_step_list:

                        # get the index of the pipeline step in the table
                        table_pipeline_step_index = np.where(
                            timinginfo_table_select['pipeline_step'] == pipeline_step)[0]
                        
                        # not all pipeline steps are in all log files
                        if len(table_pipeline_step_index) != 0:
                            html_code += """
                                    <td>{0:s}</td>
                                    """.format(timinginfo_table_select['run_time'][table_pipeline_step_index[0]])
                        else:
                            html_code += """
                                <td>N/A</td>
                                """
                    html_code += """</tr>
                            """

                html_code += """</table>
                        </div>
                    </div>\n"""
            else:
                logging.warning(
                    "Could not find timing information file {0:s} ".format(csv_file))

            # create buttons and iframes for apercal log files
            # ++++++++++++++++++++++++++++++++++++++++++++++++
            if n_log_files != 0:

                # go through the list of log files
                for log_counter in range(n_log_files):

                    log_file_list.sort()

                    frame_name = "gallery_apercal{0:d}".format(log_counter)

                    beam = os.path.basename(log_file_list[log_counter]).split(
                        "_")[0].split("apercal")[-1]

                    if beam == "":
                        log_button_name = "Apercal log"
                    else:
                        log_button_name = "Apercal log for beam {0:s}".format(
                            beam)

                    html_code += """
                        <div class="w3-container">
                            <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-dark-gray w3-hover-gray w3-margin-bottom" onclick="show_hide_plots('{0:s}')">
                                {1:s}
                            </button>
                        </div>
                         <div class="w3-container w3-margin-top w3-hide" name = "{0:s}" >
                        """.format(frame_name, log_button_name)

                    html_code += """
                        <div class="w3-container w3-large">
                            <a href="{0:s}/{1:s}">Click here to open the log file</a> if it is not shown below
                        </div>
                        <div class="w3-container">
                            <iframe class="w3-container" style="width:100%; height:1200px" src="{0:s}/{1:s}"></iframe>
                        </div>
                    </div>\n""".format(page_type, os.path.basename(log_file_list[log_counter]))

                    # # create iframe supbage
                    # html_code_iframe_page = """<!DOCTYPE HTML>
                    #     <html lang="en">

                    #     <head>
                    #     <meta http-equiv="content-type" content="text/html; charset=utf-8" />
                    #     <meta name="description" content="" />
                    #     <meta name="keywords" content="" />
                    #     </head>

                    #     <body>
                    #     <a href="{0:s}" target="_self">Click here to open log file</a>
                    #     </body>

                    #     </html>\n""".format(os.path.basename(log_file_list[log_counter]))

                    # iframe_page_name = "{0:s}/{1:s}/{2:s}".format(qa_report_obs_path, page_type, os.path.basename(
                    #     log_file_list[log_counter]).replace(".txt", ".html"))
                    # try:
                    #     logger.info(
                    #         "Writing apercal log iframe page {0:s}".format(iframe_page_name))
                    #     html_file = open(iframe_page_name, 'w')
                    #     html_file.write(html_code_iframe_page)
                    #     html_file.close()
                    # except Exception as e:
                    #     logger.error(e)
                    #     logger.error("writing iframe page content failed")
            else:
                logging.warning(
                    "No log files found for {0:s}".format(node))

            html_code += """</div>\n"""

        else:
            logging.warning(
                "No timing information and log files found for {0:s}".format(node))
            # create button
            html_code += """
                <div class="w3-container">
                    <button class="w3-btn w3-large w3-center w3-block w3-border-gray w3-amber w3-hover-yellow w3-margin-bottom w3-disabled" class="disabled" onclick="show_hide_plots('{0:s}')">
                        {1:s}
                    </button>
                </div>\n""".format(node, button_name)

        # get the csv files

    # n_log_files = len(log_file_list)

    # if n_log_files != 0:

    #     log_file_list.sort()

    #     # go through the log files and create iframes
    #     for k in range(n_log_files):

    #         # create content for iframe
    #         frame_name = "logfile{0:d}".format(k)

    #         log_file_happili = os.path.basename(
    #             log_file_list[k]).split("_")[-1].replace("txt", "")

    #         button_name = "Apercal logfile for {0:s}".format(
    #             log_file_happili)

    #         html_code += """<button onclick="show_hide_plots('{0:s}')">
    #                     {1:s}
    #                 </button>\n""".format(frame_name, button_name)

    #         html_code += """<p>
    #                 <iframe id="log" name="{0:s}" src="{1:s}/{2:s}"></iframe>
    #             </p>\n""".format(frame_name, page_type, os.path.basename(log_file_list[k]).replace(".txt", ".html"))

    #         # create iframe supbage
    #         html_code_iframe_page = """<!DOCTYPE HTML>
    #             <html lang="en">

    #             <head>
    #             <meta http-equiv="content-type" content="text/html; charset=utf-8" />
    #             <meta name="description" content="" />
    #             <meta name="keywords" content="" />
    #             </head>

    #             <body>
    #             <a href="{0:s}" target="_self">Click here to open log file</a>
    #             </body>

    #             </html>\n""".format(os.path.basename(log_file_list[k]))

    #         iframe_page_name = "{0:s}/{1:s}/{2:s}".format(qa_report_obs_path, page_type, os.path.basename(
    #             log_file_list[k]).replace(".txt", ".html"))
    #         try:
    #             logger.info(
    #                 "Writing apercal log iframe page {0:s}".format(iframe_page_name))
    #             html_file = open(iframe_page_name, 'w')
    #             html_file.write(html_code_iframe_page)
    #             html_file.close()
    #         except Exception as e:
    #             logger.error(e)
    #             logger.error("writing iframe page content failed")
    # else:
    #     logger.warning("No apercal log files found in {0:s}/{1:s}/".format(
    #         qa_report_obs_path, page_type))

    return html_code


def write_obs_content(page_name, qa_report_path, page_type='', obs_id=''):
    """
    Function to write Observation content
    """

    # empty string of html code to start with
    html_code = """"""

    # html_code = """<p>NOTE: When clicking on the buttons for the first time, please click twice (small bug)</p>"""

    qa_report_obs_path = "{0:s}/{1:s}".format(qa_report_path, obs_id)

    # create html content for subpage observing_log
    # +++++++++++++++++++++++++++++++++++++++++++++
    if page_type == 'observing_log':

        try:
            html_code = write_obs_content_observing_log(
                html_code, qa_report_obs_path, page_type)
        except Exception as e:
            logger.error(e)

    # create html content for subpage summary
    # +++++++++++++++++++++++++++++++++++++++
    if page_type == 'summary':

        try:
            html_code = write_obs_content_summary(
                html_code, qa_report_obs_path, page_type)
        except Exception as e:
            logger.error(e)

    # create html content for subpage inspection plots
    # ++++++++++++++++++++++++++++++++++++++++++++++++
    if page_type == 'inspection_plots':

        try:
            html_code = write_obs_content_inspection_plots(
                html_code, qa_report_obs_path, page_type)
        except Exception as e:
            logger.error(e)


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

    # create html content for subpage selfcal
    # ++++++++++++++++++++++++++++++++++++
    elif page_type == 'selfcal':

        try:
            html_code = write_obs_content_selfcal(
                html_code, qa_report_obs_path, page_type)
        except Exception as e:
            logger.error(e)

    # create html content for subpage continuum
    # +++++++++++++++++++++++++++++++++++++++++
    elif page_type == 'continuum':

        try:
            html_code = write_obs_content_continuum(
                html_code, qa_report_obs_path, page_type)
        except Exception as e:
            logger.error(e)

    # create html content for subpage line
    # ++++++++++++++++++++++++++++++++++++
    elif page_type == 'line':

        try:
            html_code = write_obs_content_line(
                html_code, qa_report_obs_path, page_type)
        except Exception as e:
            logger.error(e)

    # create html content for subpage mosaic
    # ++++++++++++++++++++++++++++++++++++++
    elif page_type == 'mosaic':

        try:
            html_code = write_obs_content_mosaic(
                html_code, qa_report_obs_path, page_type)
        except Exception as e:
            logger.error(e)

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
