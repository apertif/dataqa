import os
import sys
from astropy.table import Table
import logging
import glob
import time
import argparse
import socket
import report.html_report_content as hrc
# from __future__ import with_statement

logger = logging.getLogger(__name__)


def write_html_header(html_file_name, js_file, css_file=None, page_type='index', obs_id=0):
    """
    This function creates the header for an html document
    """

    if page_type == 'index':
        page_title = 'APERTIF Quality Assessment Overview'
    elif page_type == 'obs_page':
        page_title = 'Observation {0:s}'.format(obs_id)
        css_file = "../{0:s}".format(css_file)
        js_file = "../{0:s}".format(js_file)
    else:
        page_title = '{0:s} {1:s}'.format(obs_id, page_type)
        css_file = "../{0:s}".format(css_file)
        js_file = "../{0:s}".format(js_file)

    html_file = open(html_file_name, 'w')
    html_file.write("""<!DOCTYPE HTML>
    <html lang="en">
    <head>
        <title>{0}</title>
        <meta http-equiv="content-type" content="text/html; charset=utf-8" />
        <meta name="description" content="" />
        <meta name="keywords" content="" />
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
        <script src="{1}"></script>
        <link rel="stylesheet" type="text/css" href="{2}" />
    </head>
    <body>
        <div class="w3-container w3-center w3-margin-bottom w3-amber">
            <h1>{0}</h1>
        </div>\n""".format(page_title, js_file, css_file))

    html_file.close()


def write_html_end(html_file_name):
    """
    This function closes an html document
    """

    try:
        html_file = open(html_file_name, 'a')
        html_file.write("""</body>\n</html>""")
        html_file.close()
    except Exception as e:
        logger.error(e)


def write_html_obs_index(html_file_name, obs_id):
    """
    This function creates an index for the list of observations
    """

    # write the html content for the index of observations
    obs_index = """
        <div class="w3-container w3-center">
            <h2> List of Observations </h2>
            <p class="w3-center w3-container w3-large">Note: This website will allow you to go through the different qualitiy assessment products
            in addition to the apercal logfile from each node. It will not give you access to fits
            images and the source catalogue</p>
        </div>\n"""

    obs_index += """
        <div class="w3-container w3-center w3-xlarge">
            <b>{0:s}</b>
        </div>       
        <div class="w3-container w3-center">
            <div class="w3-bar w3-large w3-dark-gray">
                <a class="w3-bar-item w3-button w3-hover-yellow" href="{0:s}/{0:s}_summary.html">Summary</a>
                <a class="w3-bar-item w3-button w3-hover-yellow" href="{0:s}/{0:s}_inspection_plots.html">inspection
                    plots</a>
                <a class="w3-bar-item w3-button w3-hover-yellow"
                    href="{0:s}/{0:s}_preflag.html">preflag</a>
                <a class="w3-bar-item w3-button w3-hover-yellow"
                    href="{0:s}/{0:s}_crosscal.html">crosscal</a>
                <a class="w3-bar-item w3-button w3-hover-yellow"
                    href="{0:s}/{0:s}_selfcal.html">selfcal</a>
                <a class="w3-bar-item w3-button w3-hover-yellow"
                    href="{0:s}/{0:s}_continuum.html">continuum</a>
                <a class="w3-bar-item w3-button w3-hover-yellow" href="{0:s}/{0:s}_line.html">line</a>
                <a class="w3-bar-item w3-button w3-hover-yellow" href="{0:s}/{0:s}_mosaic.html">mosaic</a>
                <a class="w3-bar-item w3-button w3-hover-yellow" href="{0:s}/{0:s}_apercal_log.html">apercal
                    log</a>
            </div>
        </div>\n""".format(obs_id)

    try:
        html_file = open(html_file_name, 'a')
        html_file.write(obs_index)
        html_file.close()
    except Exception as e:
        logger.error(e)


def write_html_navbar(html_file_name, links, page_type='preflag', obs_id=0):
    """
    Function to add a navigation bar at the top of the website for each QA
    """

    html_code = """
        <div class="w3-top">
            <div class="w3-container w3-dark-gray w3-large">
                <div class="w3-bar">
        """
    for page in links:
        if page == page_type:
            html_code += """
                    <a class="w3-bar-item w3-button w3-hover-yellow w3-amber" href="{0:s}_{1:s}.html">{2:s}</a>\n""".format(
                obs_id, page, page.replace("_", " "))
        else:
            html_code += """
                    <a class="w3-bar-item w3-button w3-hover-yellow" href="{0:s}_{1:s}.html">{2:s}</a>\n""".format(
                obs_id, page, page.replace("_", " "))

    html_code += """
                    <a class="w3-bar-item w3-button w3-hover-yellow w3-right" href="../index.html">Overview of Observation</a>
                    <a class="w3-bar-item w3-button w3-hover-yellow w3-right" href="https://docs.google.com/document/d/1EuifDF8wwYRtaeX_jjEkUCyquP0Xwn3XPQUVVZVMoi4/edit#" target="_blank">OSA Guide</a>
                </div>
            </div>
        </div>\n"""

    try:
        html_file = open(html_file_name, 'a')
        html_file.write(html_code)
        html_file.close()
    except Exception as e:
        logger.error(e)


def write_obs_page(qa_report_path, obs_id, css_file, js_file, subpages=None):
    """
    Function to create the subpages
    """

    if subpages is not None:

        for page in subpages:

            logger.info("# Creating page {0:s}".format(page))

            page_name = "{0:s}/{1:s}/{1:s}_{2:s}.html".format(
                qa_report_path, obs_id, page)

            # create the header
            write_html_header(
                page_name, js_file, css_file=css_file, page_type=page, obs_id=obs_id)

            write_html_navbar(page_name, subpages,
                              page_type=page, obs_id=obs_id)

            hrc.write_obs_content(page_name, qa_report_path,
                                  page_type=page, obs_id=obs_id)

            # Close the index file
            write_html_end(page_name)


def create_main_html(qa_report_dir, obs_id, subpages, continuum=True, crosscal=True, line=True, mosaic=True, selfcal=True, css_file=None, js_file=None):
    """
    Function to create the main HTML file
    """

    # qa_report_dir = '{0:s}/report'.format(qa_report_dir)
    # # Check that qa_report_dir and the other directories exists
    # if not os.path.exists(qa_report_dir):
    #     logger.warning(
    #         "Directory {0:s} does not exists. Abort".format(qa_report_dir))
    #     logger.info("Creating directory {0:s}".format(qa_report_dir))
    #     os.mkdir(qa_report_dir)
    # else:
    #     logger.info("Directory {0:s} exists".format(qa_report_dir))

    # if continuum:
    #     if not os.path.exists('{0:s}/continuum'.format(qa_report_dir):
    #         logger.error("Directory for continuum does not exists")
    #         return -1

    # if crosscal:
    #     if not os.path.exists('{0:s}/crosscal'.format(qa_report_dir):
    #         logger.error("Directory for crosscal does not exists")
    #         return -1

    # if line:
    #     if not os.path.exists('{0:s}/line'.format(qa_report_dir):
    #         logger.error("Directory for line does not exists")
    #         return -1

    # if mosaic:
    #     if not os.path.exists('{0:s}/mosaic'.format(qa_report_dir):
    #         logger.error("Directory for mosaic does not exists")
    #         return -1

    # if selfcal:
    #     if not os.path.exists('{0:s}/selfcal'.format(qa_report_dir):
    #         logger.error("Directory for selfcal does not exists")
    #         return -1

    # get a list of observations in this directory
    # obs_dir_list = glob.glob('{0:s}/{1:s}'.format(qa_report_dir, '[0-9]'*9))

    # if len(obs_dir_list) == 0:
    #     obs_dir_list =[obs_id]
    #     logger.error("No observation found in QA directory. Abort")

    # obs_dir_list.sort()

    # obs_ids = [os.path.basename(obs) for obs in obs_dir_list]

    # number of obs_ids
    # n_obs_ids = len(obs_dir_list)

    # Create index file
    # +++++++++++++++++
    index_file = '{0:s}/index.html'.format(qa_report_dir)
    logging.info("## Creating index file: {0:s}".format(index_file))

    # create the header
    write_html_header(index_file, os.path.basename(css_file),
                      os.path.basename(js_file), page_type='index')

    # Add a list of Observations
    write_html_obs_index(index_file, obs_id)

    # Close the index file
    write_html_end(index_file)

    # Creating subpages
    # +++++++++++++++++
    logging.info("## Writing subpages for observation {0:s}".format(obs_id))

    # obs_report_path = '{0:s}/{1:s}'.format(qa_report_dir, obs_ids[k])

    try:
        write_obs_page(qa_report_dir, obs_id, os.path.basename(css_file),
                       os.path.basename(js_file), subpages=subpages)
    except Exception as e:
        logger.error(e)
