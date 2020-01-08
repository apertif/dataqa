from crosscal_plots import GDSols


def get_dish_delay_plots(obs_id, fluxcal, basedir=None):
    """
    Simple function to plot the dish delay.
    This needs to run separately from the other crosscal plots because
    it requires all 40 beams to be accessible

    | Args:
    |   obs_id (int): Taskid of the observation
    |   fluxcal (str): Name of the flux calibrator
    |   basedir (str): Optional directory of the taskid
    """

    GD = GDSols(obs_id, fluxcal, False, basedir=basedir)
    GD.get_data()
    GD.plot_dish_delay()
