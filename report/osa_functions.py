# test script for jupyter notebook OSA report
import numpy as np
import os
import shutil
from astropy.table import Table, join
from ipywidgets import widgets, Layout
from IPython.display import display
import glob


def run():

    layout_select = Layout(width='30%')
    layout_area = Layout(width='60%', height='100px')
    style = {'description_width': 'initial'}

    # get the table file (there should only be one)
    # get the current director
    cwd = os.getcwd()
    # get the obs id
    obs_id = cwd.split("/")[-3]
    obs_file = "../{}_obs.ecsv".format(obs_id)

    prepare_label = widgets.HTML(
        value="<h2 style='text-decoration: underline'> Observation and OSA </h2>"
    )
    display(prepare_label)

    obs_text = widgets.Text(value=obs_id,
                            placeholder='',
                            description='Obs ID:',
                            disabled=False,
                            layout=layout_select)

    display(obs_text)

    if not os.path.exists(obs_file):
        # technically it is not necssary to have this file here
        print("Warning: Could not find observation information. Please provide your name")

        osa_text = widgets.Text(value='',
                                placeholder='',
                                description='OSA:',
                                disabled=False,
                                layout=layout_select)
        display(osa_text)
    else:
        obs_table = Table.read(obs_file, format="ascii.ecsv")

        osa_text = widgets.Text(value=obs_table['OSA'][0],
                                placeholder='',
                                description='OSA:',
                                disabled=False,
                                layout=layout_select)
        display(osa_text)

    dropdown_options = ['unchecked', 'unknown',
                        'failed', 'bad', 'acceptable',  'good']

    dropdown_options = ['Unchecked', 'Unknown',
                        'Critical', 'Bad', 'Acceptable', 'Good', 'Excellent']

    status_legend_prepare = "<p style='font-weight:bold'>Status legend:</p> Excellent: 100% (0 beams missing); Good: 95% (1-2 beams missing); Acceptable: 85% (3-6 beams missing); Bad: 75% (7-10 beams missing); Critical: <75% (More than 10 beams missing); Unknown (No information available)</p>"
    status_legend_preflag = "<p style='font-weight:bold'>Status legend:</p> Excellent: 100% (0 beams failed); Good: 95% (1-2 beams failed); Acceptable: 85% (3-6 beams failed); Bad: 75% (7-10 beams failed); Critical: <75% (More than 10 beams failed); Unknown (No information available)</p>"
    status_legend_crosscal = status_legend_preflag
    status_legend_selfcal = "<p style='font-weight:bold'>Status legend:</p> Excellent: 100% (No issues or failed beams); Good: 95% (1-2 beams show issues or failed); Acceptable: 85% (3-6 beams show issues or failed); Bad: 75% (7-10 beams show issues); Critical: <75% (More than 10 beams show issues); Unknown (No information available)</p>"
    status_legend_continuum = status_legend_selfcal
    status_legend_polarisation = status_legend_selfcal
    status_legend_line = status_legend_selfcal
    status_legend_summary = status_legend_selfcal

    # Prepare
    # =======
    prepare_label = widgets.HTML(
        value="<h2 style='text-decoration: underline'> Prepare </h2>"
    )
    display(prepare_label)

    prepare_label_info = widgets.HTML(
        value=status_legend_prepare)
    #    value="Status legend: Excellent: 100% (0 beams missing)")
    display(prepare_label_info)

    prepare_menu = widgets.Dropdown(options=dropdown_options,
                                    value='Unchecked',
                                    description='Status:',
                                    disabled=False,
                                    layout=layout_select)
    display(prepare_menu)

    prepare_notes = widgets.Textarea(value='-',
                                     placeholder='Nothing to add',
                                     description='Notes:',
                                     disabled=False,
                                     layout=layout_area)
    display(prepare_notes)

    # Preflag
    # =======
    preflag_label = widgets.HTML(
        value="<h2 style='text-decoration: underline'> Preflag </h2>")
    display(preflag_label)

    preflag_label_info = widgets.HTML(
        value=status_legend_preflag)
    #    value="Status legend: Excellent: 100% (0 beams missing)")
    display(preflag_label_info)

    preflag_menu = widgets.Dropdown(options=dropdown_options,
                                    value='Unchecked',
                                    description='Select:',
                                    disabled=False,
                                    layout=layout_select)
    display(preflag_menu)

    preflag_notes = widgets.Textarea(value='-',
                                     placeholder='Nothing to add',
                                     description='Notes:',
                                     disabled=False,
                                     layout=layout_area)
    display(preflag_notes)

    # Crosscal
    # ========
    crosscal_label = widgets.HTML(
        value="<h2 style='text-decoration: underline'> Crosscal </h2>")
    display(crosscal_label)

    crosscal_label_info = widgets.HTML(
        value=status_legend_crosscal)
    display(crosscal_label_info)

    crosscal_menu = widgets.Dropdown(options=dropdown_options,
                                     value='Unchecked',
                                     description='Select:',
                                     disabled=False,
                                     layout=layout_select)
    display(crosscal_menu)

    crosscal_notes = widgets.Textarea(value='-',
                                      placeholder='Nothing to add',
                                      description='Notes:',
                                      disabled=False,
                                      layout=layout_area)
    display(crosscal_notes)

    # Selfcal
    # ========
    selfcal_label = widgets.HTML(
        value="<h2 style='text-decoration: underline'> Selfcal </h2>")
    display(selfcal_label)

    selfcal_label_info = widgets.HTML(
        value=status_legend_selfcal)
    display(selfcal_label_info)

    selfcal_menu = widgets.Dropdown(options=dropdown_options,
                                    value='Unchecked',
                                    description='Select:',
                                    disabled=False,
                                    layout=layout_select)
    display(selfcal_menu)

    selfcal_notes = widgets.Textarea(value='-',
                                     placeholder='Nothing to add',
                                     description='Notes:',
                                     disabled=False,
                                     layout=layout_area)
    display(selfcal_notes)

    # Continuum
    # =========
    continuum_label = widgets.HTML(
        value="<h2 style='text-decoration: underline'> Continuum </h2>")
    display(continuum_label)

    continuum_label_info = widgets.HTML(
        value=status_legend_continuum)
    display(continuum_label_info)

    continuum_menu = widgets.Dropdown(options=dropdown_options,
                                      value='Unchecked',
                                      description='Select:',
                                      disabled=False,
                                      layout=layout_select)
    display(continuum_menu)

    continuum_notes = widgets.Textarea(value='-',
                                       placeholder='Nothing to add',
                                       description='Notes:',
                                       disabled=False,
                                       layout=layout_area)
    display(continuum_notes)

    # Polarisation
    # ============
    polarisation_label = widgets.HTML(
        value="<h2 style='text-decoration: underline'> Polarisation </h2>")
    display(polarisation_label)

    polarisation_label_info = widgets.HTML(
        value=status_legend_polarisation)
    display(polarisation_label_info)

    polarisation_menu = widgets.Dropdown(options=dropdown_options,
                                         value='Unchecked',
                                         description='Select:',
                                         disabled=False,
                                         layout=layout_select)
    display(polarisation_menu)

    polarisation_notes = widgets.Textarea(value='-',
                                          placeholder='Nothing to add',
                                          description='Notes:',
                                          disabled=False,
                                          layout=layout_area)
    display(polarisation_notes)

    # Line
    # ====
    line_label = widgets.HTML(
        value="<h2 style='text-decoration: underline'> Line </h2>")
    display(line_label)

    line_label_info = widgets.HTML(
        value=status_legend_line)
    display(line_label_info)

    line_menu = widgets.Dropdown(options=dropdown_options,
                                 value='Unchecked',
                                 description='Select:',
                                 disabled=False,
                                 layout=layout_select)
    display(line_menu)

    line_notes = widgets.Textarea(value='-',
                                  placeholder='Nothing to add',
                                  description='Notes:',
                                  disabled=False,
                                  layout=layout_area)
    display(line_notes)

    # Summary
    # =======
    summary_label = widgets.HTML(
        value="<h2 style='text-decoration: underline'> Summary </h2>")
    display(summary_label)

    summary_label_info = widgets.HTML(
        value=status_legend_summary)
    display(summary_label_info)

    summary_menu = widgets.Dropdown(options=dropdown_options,
                                    value='Unchecked',
                                    description='Select:',
                                    disabled=False,
                                    layout=layout_select)
    display(summary_menu)

    # notes_label = widgets.Label("#### Notes")
    # display(notes_label)
    summary_notes = widgets.Textarea(value='-',
                                     placeholder='Nothing to add',
                                     description='Summary:',
                                     disabled=False,
                                     layout=layout_area)
    display(summary_notes)

    btn = widgets.Button(description='Save', button_style='primary')
    display(btn)

    def show_warning_label(module, request_info=False):
        if request_info:
            warning_label = widgets.HTML(
                value="<p style='font-size:large; color:red'> Cannot save report. You have selected a status other then <i> Excellent </i> for <i>{0}</i>. Please provide at least the beam numbers and if possible a short statement </p>".format(module))
            display(warning_label)
        else:
            warning_label = widgets.HTML(
                value="<p style='font-size:large; color:red'> Cannot save report. Please choose status for <i>{0}</i> </p>".format(module))
            display(warning_label)

    def save_info(b):

        # Check that a name has been entered for the OSA (depracted)
        # and that each of the pipeline steps have been checked
        if obs_text.value == '':
            warning_label = widgets.HTML(
                value="<p style='font-size:large; color:red'> Cannot save report. Please enter your Obs ID </p>")
            display(warning_label)
            return -1
        if osa_text.value == '':
            warning_label = widgets.HTML(
                value="<p style='font-size:large; color:red'> Cannot save report. Please enter your name </p>")
            display(warning_label)
            return -1

        if prepare_menu.value == 'Unchecked':
            show_warning_label("Prepare")
        elif prepare_menu.value != 'Excellent' and prepare_notes.value == "-":
            show_warning_label("Prepare", request_info=True)
            return -1

        if preflag_menu.value == 'Unchecked':
            show_warning_label("Preflag")
            return -1
        elif preflag_menu.value != 'Excellent' and preflag_notes.value == "-":
            show_warning_label("Preflag", request_info=True)
            return -1

        if crosscal_menu.value == 'Unchecked':
            show_warning_label("Crosscal")
            return -1
        elif crosscal_menu.value != 'Excellent' and crosscal_notes.value == "-":
            show_warning_label("Crosscal", request_info=True)
            return -1

        if selfcal_menu.value == 'Unchecked':
            show_warning_label("Selfcal")
            return -1
        elif selfcal_menu.value != 'Excellent' and selfcal_notes.value == "-":
            show_warning_label("Selfcal", request_info=True)
            return -1

        if continuum_menu.value == 'Unchecked':
            show_warning_label("Continuum")
            return -1
        elif continuum_menu.value != 'Excellent' and continuum_notes.value == "-":
            show_warning_label("Continuum", request_info=True)
            return -1

        if polarisation_menu.value == 'Unchecked':
            show_warning_label("Polarisation")
            return -1
        elif polarisation_menu.value != 'Excellent' and polarisation_notes.value == "-":
            show_warning_label("Polarisation", request_info=True)
            return -1

        if line_menu.value == 'Unchecked':
            show_warning_label("Line")
            return -1
        elif line_menu.value != 'Excellent' and line_notes.value == "-":
            show_warning_label("Line", request_info=True)
            return -1

        if summary_menu.value == 'Unchecked':
            show_warning_label("Summary")
            return -1
        elif summary_menu.value != 'Excellent' and summary_notes.value == "-":
            show_warning_label("Summary", request_info=True)
            return -1

        # create the table
        summary_table = Table([
            [obs_text.value],
            [osa_text.value],
            [prepare_menu.value],
            [prepare_notes.value],
            [preflag_menu.value],
            [preflag_notes.value],
            [crosscal_menu.value],
            [crosscal_notes.value],
            [selfcal_menu.value],
            [selfcal_notes.value],
            [continuum_menu.value],
            [continuum_notes.value],
            [polarisation_menu.value],
            [polarisation_notes.value],
            [line_menu.value],
            [line_notes.value],
            [summary_menu.value],
            [summary_notes.value]], names=(
            'Obs_ID', 'OSA', 'prepare', 'prepare_notes', 'preflag', 'preflag_notes', 'crosscal', 'crosscal_notes', 'selfcal', 'selfcal_notes', 'continuum', 'continuum_notes', 'polarisation', 'polarisation_notes', 'line', 'line_notes', 'summary', 'summary_notes'))

        table_name = "{0}_OSA_report.ecsv".format(obs_id)

        try:
            summary_table.write(
                table_name, format='ascii.ecsv', overwrite=True)
        except:
            warning_save_table_label = widgets.HTML(
                value="<p style='font-size:large; color:red'> ERROR: Could not save report. Please ask for help.</p>")
            display(warning_save_table_label)
        else:
            save_table_label = widgets.HTML(
                value="<p style='font-size:large; color:green'> Saved OSA report {0:s}. Thank You.</p>".format(table_name))
            display(save_table_label)

        # copy the file to the collection directory
        table_copy = "/data/apertif/qa/OSA_reports/{0}".format(table_name)
        try:
            shutil.copy2(table_name, table_copy)
        except:
            warning_copy_table_label = widgets.HTML(
                value="<p style='font-size:large; color:red'> ERROR: Could not create back up of report. Please ask for help</p>")
            display(warning_copy_table_label)
        else:
            copy_table_label = widgets.HTML(
                value="<p style='font-size:large; color:green'> Created backup of OSA report.</p>".format(table_name))
            display(copy_table_label)
            print("Created backup of OSA report")

    btn.on_click(save_info)
