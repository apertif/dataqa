# test script for jupyter notebook OSA report
import numpy as np
import os
import shutil
from astropy.table import Table, join
from ipywidgets import widgets
from IPython.display import display
import glob


def run():

    # get the table file (there should only be one)
    # get the current director
    cwd = os.getcwd()
    # get the obs id
    obs_id = cwd.split("/")[-2]
    obs_file = "../{}_obs.ecsv".format(obs_id)
    if not os.path.exists(obs_file):
        # technically it is not necssary to have this file here
        print("ERROR: Could not find observation information. Abort")
        return -1

    test_table = Table.read(obs_file, format="ascii.ecsv")

    obsid_label = widgets.Label("Obs ID: {}".format(test_table['Obs_ID'][0]))
    display(obsid_label)
    # obsid_text = widgets.Text()
    # display(obsid_text)

    #osa_label = widgets.Label("OSA")
    # display(osa_label)
    osa_text = widgets.Text(value=test_table['OSA'][0],
                            placeholder='',
                            description='OSA:',
                            disabled=False)
    display(osa_text)

    dropdown_options = ['unchecked', 'unknown',
                        'failed', 'bad', 'acceptable',  'good']

    # Preflag
    # =======
    preflag_menu = widgets.Dropdown(options=dropdown_options,
                                    value='unchecked',
                                    description='Preflag:',
                                    disabled=False)
    display(preflag_menu)

    preflag_notes = widgets.Textarea(value='-',
                                     placeholder='Nothing to add',
                                     description='Preflag notes:',
                                     disabled=False)
    display(preflag_notes)

    # Crosscal
    # ========
    crosscal_menu = widgets.Dropdown(options=dropdown_options,
                                     value='unchecked',
                                     description='Crosscal:',
                                     disabled=False)
    display(crosscal_menu)

    crosscal_notes = widgets.Textarea(value='-',
                                      placeholder='Nothing to add',
                                      description='Crosscal notes:',
                                      disabled=False)
    display(crosscal_notes)

    # Selfcal
    # ========
    selfcal_menu = widgets.Dropdown(options=dropdown_options,
                                    value='unchecked',
                                    description='Selfcal:',
                                    disabled=False)
    display(selfcal_menu)

    selfcal_notes = widgets.Textarea(value='-',
                                     placeholder='Nothing to add',
                                     description='Selfcal notes:',
                                     disabled=False)
    display(selfcal_notes)

    # Continuum
    # =========
    continuum_menu = widgets.Dropdown(options=dropdown_options,
                                      value='unchecked',
                                      description='Continuum:',
                                      disabled=False)
    display(continuum_menu)

    continuum_notes = widgets.Textarea(value='-',
                                       placeholder='Nothing to add',
                                       description='Continuum notes:',
                                       disabled=False)
    display(continuum_notes)

    # Polarisation
    # ============
    polarisation_menu = widgets.Dropdown(options=dropdown_options,
                                         value='unchecked',
                                         description='Polarisation:',
                                         disabled=False)
    display(polarisation_menu)

    polarisation_notes = widgets.Textarea(value='-',
                                          placeholder='Nothing to add',
                                          description='Polarisation notes:',
                                          disabled=False)
    display(polarisation_notes)

    # Line
    # ====
    line_menu = widgets.Dropdown(options=dropdown_options,
                                 value='unchecked',
                                 description='Line:',
                                 disabled=False)
    display(line_menu)

    line_notes = widgets.Textarea(value='-',
                                  placeholder='Nothing to add',
                                  description='Line notes:',
                                  disabled=False)
    display(line_notes)

    summary_menu = widgets.Dropdown(options=dropdown_options,
                                    value='unchecked',
                                    description='Summary:',
                                    disabled=False)
    display(summary_menu)

    #notes_label = widgets.Label("Notes")
    # display(notes_label)
    notes_text = widgets.Textarea(value='-',
                                  placeholder='Nothing to add',
                                  description='Summary:',
                                  disabled=False)
    display(notes_text)

    btn = widgets.Button(description='Save')
    display(btn)

    def save_info(b):

        # Check that a name has been entered for the OSA (depracted)
        # and that each of the pipeline steps have been checked
        if osa_text.value == '':
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
                [test_table['Obs_ID'][0]],
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

            table_name = "{0}_OSA_report.ecsv".format(test_table['Obs_ID'][0])
            summary_table.write(
                table_name, format='ascii.ecsv', overwrite=True)

            print("Saved OSA report {0:s}. Thank you.".format(table_name))

            # copy the file to the collection directory
            table_copy = "/data/apertif/qa/OSA_reports/{0}".format(table_name)
            shutil.copy2(table_name, table_copy)

    btn.on_click(save_info)
