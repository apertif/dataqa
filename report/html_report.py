import os
import sys
from astropy.table import Table
import logging
import glob
import time
import argparse
import socket
import html_report_content as hrc
# from __future__ import with_statement


def write_html_header(html_file_name, page_type='index', css_style=None, js_file=None, obs_id=0):
    """
    This function creates the header for an html document
    """

    if css_style is None:
        css_style = "/home/schulz/Software/apercal/dataqa/dataqa/report/report_style.css"

    if js_file is None:
        js_file = "/home/schulz/Software/apercal/dataqa/dataqa/report/report_fct.js"

    if page_type == 'index':
        page_title = 'APERTIF Science Demonstration Overview'
    elif page_type == 'obs_page':
        page_title = 'Observation {0:d}'.format(obs_id)
    else:
        page_title = '{0:d} {1:s}'.format(obs_id, page_type)

    html_file = open(html_file_name, 'w')
    html_file.write("""<!DOCTYPE HTML>
        <html lang="en">
        <head>
            <title>APERTIF Science Demonstration 2019</title>
            <meta http-equiv="content-type" content="text/html; charset=utf-8" />
	        <meta name="description" content="" />
	        <meta name="keywords" content="" />
            <script src="{0}"></script>
            <link rel="stylesheet" type="text/css" href="{1}" />
        </head>
        <body>
            <h1>{2:s}</h1>\n""".format(js_file, css_style, page_title))

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
        logging.error(e)


def write_html_obs_index(html_file_name, obs_id):
    """
    This function creates an index for the list of observations
    """

    # write the html content for the index of observations
    obs_index = """<div id="obs_index">
        <h2> List of Observations </h2>
        <table class="obs_index">\n"""

    # <table class = "reportTable" >
    #         <tr >
    #             <th > SBID < /th >
    #             <th > Project < /th >
    #             <th > Date < /th >
    #             <th > Duration < br > (hours) < /th >
    #             <th > Field Centre < /th >
    #             <th > Central Frequency < br > (MHz) < /th >
    #         </tr >
    #         <tr >
    #                 <td > {0} < /td >
    #                 <td > {1} < /td >
    #                 <td > {2} < /td >
    #                 <td > {3} < /td >
    #                 <td > {4} < /td >
    #                 <td > {5: .2f} < /td >
    #                 </tr >
    #     </table

    obs_index += """<tr>
            <th colspan="7">{0:d}</th>
        </tr>
        <tr>
            <td > <a href="{0:d}/{0:d}_prepare.html">prepare</a> </td>
            <td > <a href="{0:d}/{0:d}_crosscal.html">crosscal</a> </td>
            <td > <a href="{0:d}/{0:d}_selfcal.html">selfcal</a> </td>
            <td > <a href="{0:d}/{0:d}_continuum.html">continuum</a> </td>
            <td > <a href="{0:d}/{0:d}_line.html">line</a> </td>
            <td > <a href="{0:d}/{0:d}_mosaic.html">mosaic</a> </td>
            <td > <a href="{0:d}/{0:d}_apercal_log.html">apercal.log</a> </td>
        </tr>\n""".format(obs_id)

    obs_index += """</table>
        </div>\n"""

    try:
        html_file = open(html_file_name, 'a')
        html_file.write(obs_index)
        html_file.close()
    except Exception as e:
        logging.error(e)


def write_html_navbar(html_file_name, links, page_type='preflag', obs_id=0):
    """
    Function to add a navigation bar at the top of a sight
    """

    html_code = """
        <ul>
            <li style="float:right"><a href="index.html">List of Observations</a></li>
        """
    for page in links:
        if page == page_type:
            html_code += """<li><a class="active" href="{0:d}_{1:s}.html">{1:s}</a></li>\n""".format(
                obs_id, page)
        else:
            html_code += """<li><a href="{0:d}_{1:s}.html">{1:s}</a></li>\n""".format(
                obs_id, page)

    html_code += """</ul>\n"""

    try:
        html_file = open(html_file_name, 'a')
        html_file.write(html_code)
        html_file.close()
    except Exception as e:
        logging.error(e)
        print("ERROR")


def write_obs_page(qa_report_path, obs_id, subpages=None):
    """
    Function to create the subpages
    """

    if subpages is not None:

        for page in subpages:

            print("   Creating page {0:s}".format(page))

            page_name = "{0:s}/{1:d}/{1:d}_{2:s}.html".format(
                qa_report_path, obs_id, page)

            # create the header
            write_html_header(
                page_name, page_type=page, obs_id=obs_id)

            write_html_navbar(page_name, subpages,
                              page_type=page, obs_id=obs_id)

            hrc.write_obs_content(page_name, qa_report_path,
                                  page_type=page, obs_id=obs_id)

            # Close the index file
            write_html_end(page_name)


def create_main_html(qa_dir, obs_id, subpages, continuum=True, crosscal=True, line=True, mosaic=True, selfcal=True):
    """
    Function to create the main HTML file
    """

    qa_report_dir = '{0:s}/report'.format(qa_dir)
    # Check that qa_dir and the other directories exists
    if not os.path.exists(qa_report_dir):
        logging.warning(
            "Directory {0:s} does not exists. Abort".format(qa_report_dir))
        logging.info("Creating directory {0:s}".format(qa_dir))
        os.mkdir(qa_report_dir)
    else:
        logging.info("Directory {0:s} exists".format(qa_report_dir))

    # if continuum:
    #     if not os.path.exists('{0:s}/continuum'.format(qa_dir):
    #         logging.error("Directory for continuum does not exists")
    #         return -1

    # if crosscal:
    #     if not os.path.exists('{0:s}/crosscal'.format(qa_dir):
    #         logging.error("Directory for crosscal does not exists")
    #         return -1

    # if line:
    #     if not os.path.exists('{0:s}/line'.format(qa_dir):
    #         logging.error("Directory for line does not exists")
    #         return -1

    # if mosaic:
    #     if not os.path.exists('{0:s}/mosaic'.format(qa_dir):
    #         logging.error("Directory for mosaic does not exists")
    #         return -1

    # if selfcal:
    #     if not os.path.exists('{0:s}/selfcal'.format(qa_dir):
    #         logging.error("Directory for selfcal does not exists")
    #         return -1

    # get a list of observations in this directory
    # obs_dir_list = glob.glob('{0:s}/{1:s}'.format(qa_dir, '[0-9]'*9))

    # if len(obs_dir_list) == 0:
    #     obs_dir_list =[obs_id]
    #     logging.error("No observation found in QA directory. Abort")

    # obs_dir_list.sort()

    # obs_ids = [os.path.basename(obs) for obs in obs_dir_list]

    # number of obs_ids
    # n_obs_ids = len(obs_dir_list)

    # Create index file
    # +++++++++++++++++
    index_file = '{0:s}/index.html'.format(qa_report_dir)

    # create the header
    write_html_header(index_file, page_type='index')

    # Add a list of Observations
    write_html_obs_index(index_file, obs_id)

    # Close the index file
    write_html_end(index_file)

    print("Writing subpages for observation {0:d}".format(obs_id))

    # obs_report_path = '{0:s}/{1:s}'.format(qa_report_dir, obs_ids[k])

    write_obs_page(qa_report_dir, obs_id, subpages=subpages)

    return 1
