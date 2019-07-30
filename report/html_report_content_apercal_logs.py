import os
import sys
from astropy.table import Table
import logging
import glob
import time
import socket
import numpy as np

logger = logging.getLogger(__name__)


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
                Please note that there is an issue with reading the timing information which is why they are
                incorrect for prepare and polarisation.
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

                pipeline_step_list = ["start_pipeline", "prepare",
                                      "preflag", "ccal", "convert", "scal", "continuum", "line", "transfer"]

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
                    timinginfo_table_select = timinginfo_table[np.where(
                        timinginfo_table['beam'] == timinginfo_beam)]

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
                        line = os.path.basename(log_file_list[log_counter]).split(
                            "_")[1]
                        if line == "line":
                            log_button_name = "Apercal log for line"
                        else:
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
