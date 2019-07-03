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

    # Preflag
    # =======
    preflag_label = widgets.Label("Preflag")
    display(preflag_label)

    preflag_menu = widgets.Dropdown(options=dropdown_options,
                                    value='unchecked',
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
    crosscal_label = widgets.Label("Crosscal")
    display(crosscal_label)

    crosscal_menu = widgets.Dropdown(options=dropdown_options,
                                     value='unchecked',
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
    selfcal_label = widgets.Label("Selfcal")
    display(selfcal_label)

    selfcal_menu = widgets.Dropdown(options=dropdown_options,
                                    value='unchecked',
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
    continuum_label = widgets.Label("Continuum")
    display(continuum_label)

    continuum_menu = widgets.Dropdown(options=dropdown_options,
                                      value='unchecked',
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
    polarisation_label = widgets.Label("Polarisation")
    display(polarisation_label)

    polarisation_menu = widgets.Dropdown(options=dropdown_options,
                                         value='unchecked',
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
    line_label = widgets.Label("Line")
    display(line_label)

    line_menu = widgets.Dropdown(options=dropdown_options,
                                 value='unchecked',
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
    summary_label = widgets.Label("Overall")
    display(summary_label)

    summary_menu = widgets.Dropdown(options=dropdown_options,
                                    value='unchecked',
                                    description='Select:',
                                    disabled=False,
                                    layout=layout_select)
    display(summary_menu)

    #notes_label = widgets.Label("Notes")
    # display(notes_label)
    notes_text = widgets.Textarea(value='-',
                                  placeholder='Nothing to add',
                                  description='Summary:',
                                  disabled=False,
                                  layout=layout_area)
    display(notes_text)

    btn = widgets.Button(description='Save', button_style='primary')
    display(btn)

    def save_info(b):

        # Check that a name has been entered for the OSA (depracted)
        # and that each of the pipeline steps have been checked
        if obs_text.value == '':
            print('\x1b[31m{0:s}\x1b[0m'.format(
                "Cannot save report. Please enter Obs ID"))
            return -1
        elif osa_text.value == '':
            print('\x1b[31m{0:s}\x1b[0m'.format(
                "Cannot save report. Please enter your name"))
            return -1
        elif preflag_menu.value == 'unchecked':
            print('\x1b[31m{0:s}\x1b[0m'.format(
                "Cannot save report. Please choose a statement for preflag"))
            return -1
        elif crosscal_menu.value == 'unchecked':
            print('\x1b[31m{0:s}\x1b[0m'.format(
                "Cannot save report. Please choose a statement for crosscal"))
            return -1
        elif selfcal_menu.value == 'unchecked':
            print('\x1b[31m{0:s}\x1b[0m'.format(
                "Cannot save report. Please choose a statement for selfcal"))
            return -1
        elif continuum_menu.value == 'unchecked':
            print('\x1b[31m{0:s}\x1b[0m'.format(
                "Cannot save report. Please choose a statement for continuum"))
            return -1
        elif polarisation_menu.value == 'unchecked':
            print('\x1b[31m{0:s}\x1b[0m'.format(
                "Cannot save report. Please choose a statement for polarisation"))
            return -1
        elif line_menu.value == 'unchecked':
            print('\x1b[31m{0:s}\x1b[0m'.format(
                "Cannot save report. Please choose a statement for line"))
            return -1
        elif summary_menu.value == 'unchecked':
            print('\x1b[31m{0:s}\x1b[0m'.format(
                "Cannot save report. Please choose a statement for summary"))
            return -1
        else:
            # create the table
            summary_table = Table([
                [obs_text.value],
                [osa_text.value],
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
                [notes_text.value]], names=(
                'Obs_ID', 'OSA', 'preflag', 'preflag_notes', 'crosscal', 'crosscal_notes', 'selfcal', 'selfcal_notes', 'continuum', 'continuum_notes', 'polarisation', 'polarisation_notes', 'line', 'line_notes', 'summary', 'notes'))

            table_name = "{0}_OSA_report.ecsv".format(obs_id)

            try:
                summary_table.write(
                    table_name, format='ascii.ecsv', overwrite=True)
            except:
                print("ERROR: Could not save report. Please ask for help")
            else:
                print("Saved OSA report {0:s}. Thank You.".format(table_name))

            # copy the file to the collection directory
            table_copy = "/data/apertif/qa/OSA_reports/{0}".format(table_name)
            try:
                shutil.copy2(table_name, table_copy)
            except:
                print("ERROR: Could not create back up of report. Please ask for help")
            else:
                print("Created backup of OSA report")

    btn.on_click(save_info)
