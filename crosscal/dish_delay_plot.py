"""
Simple function to plot the dish delay.
This needs to run separately from the other crosscal plots because
it requires all 40 beams to be accessible
"""

from crosscal_plots import GDSols


def get_dish_delay_plots(obs_id, fluxcal, basedir=None):

    GD = GDSols(obs_id, fluxcal, False, basedir=basedir)
    GD.get_data()
    GD.plot_dish_delay()
