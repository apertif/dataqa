# test script for jupyter notebook OSA report
import numpy as np
from astropy.table import Table, join
from ipywidgets import widgets
from IPython.display import display


def run():

    # open the table
    test_table = Table.read("obs.ecsv", format="ascii.ecsv")

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

        # Check the
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
        elif line_menu.value == 'unchecked':
            print('\x1b[31m{0:s}\x1b[0m'.format(
                "Cannot save report. Please choose a statement for line"))
            return -1
        elif summary_menu.value == 'unchecked':
            print('\x1b[31m{0:s}\x1b[0m'.format(
                "Cannot save report. Please choose a statement for summary"))
            return -1
        else:
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

    btn.on_click(save_info)
