#Get summary of reports from json files

from __future__ import print_function

__author__="E.A.K. Adams"

"""
Functions for getting quick
overview of OSA reports.
End-goal is to produce nice
(google?) spreadsheets.
For now, just print summaries
to screen (for monthly report)
"""

#import needed packages
import json
import os
import glob

#get list of all reports
report_list = glob.glob('/data/apertif/qa/OSA_reports/*json')

#iterate through each report
for report in report_list:
    with open(report) as report_file:
        report_data = json.load(report_file)
        #get the highlight out
        overall_status = report_data['Summary']['Status']
        #get scan id
        scanid = report[29:38]
        print(('Scan {0} has an overall status '
               'of {1}').format(scanid,overall_status))
