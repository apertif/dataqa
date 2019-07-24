# inspect_beamweights: Make plots of beam weights from any observation
# K.M.Hess 27/06/2019 (hess@astro.rug.nl)
# adapted for dataQA by Robert Schulz
__author__ = "Tammo Jan Dijkema & Kelley M. Hess & Robert Schulz"
__date__ = "$23-jul-2019 16:00:00$"
__version__ = "0.3"

from argparse import ArgumentParser, RawTextHelpFormatter
import casacore.tables as pt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scandata import get_default_imagepath
import os
import pymp
from apercal.libs import lib
import logging
import glob

###################################################################


def parse_args():

    parser = ArgumentParser(description="Plot beam weights for a given scan.",
                            formatter_class=RawTextHelpFormatter)

    parser.add_argument('obs_id', type=str,
                        help='Specify the task ID number')
    parser.add_argument('calibrator', type=str,
                        help='Specify the calibrator.')
    parser.add_argument('-b', '--beam', type=int,
                        help='Specify the beam to plot. (default: %(default)s).')
    parser.add_argument('--subband_step', default=10, type=int,
                        help='Take every subband_step-th subband. (default: %(default)s).')
    parser.add_argument('--base_dir', type=str,
                        help='Specify the base directory (default: %(default)s).')
    parser.add_argument("-p", "--path", type=str,
                        help='Path to QA output')
    parser.add_argument("-t", "--threads", default=1, type=int,
                        help='Number of threads to use (default: %(default)s).')

    args = parser.parse_args()
    return args


def convert_weights(mat):
    """Converts 2x64 array to 11x11 array with apertif numbering"""
    # test = np.chararray((11,11), itemsize=3)
    converted_mat = np.zeros((11, 11), dtype=np.complex64)
    for el_num in range(61):
        for x_or_y_num, x_or_y_letter in enumerate(['X', 'Y']):
            if x_or_y_letter == 'Y' and el_num == 60:
                break
            # test[give_coord(x_or_y_letter, el_num)] = "{:02d}".format(el_num) + x_or_y_letter
            converted_mat[give_coord(x_or_y_letter, el_num)
                          ] = mat[x_or_y_num, el_num]
    return converted_mat


def give_coord(x_or_y, el_num):
    """Give the x and y position for an apertif antenna element

    Args:
        x_or_y (str): Polarization 'X' or 'Y'
        el_num (int): antenna number from 0 to 61 (X) or 60 (Y)

    Returns:
        Tuple[int, int]: y and x coordinates
    """
    if el_num < 55:
        y_coord = (el_num % 11)
        if y_coord % 2 == 0:
            x_coord = (el_num // 11) * 2 + (x_or_y == 'Y')
        else:
            x_coord = (el_num // 11) * 2 + (x_or_y == 'X')
    else:
        y_coord = (el_num - 55) * 2 + (x_or_y == 'Y')
        x_coord = 10
    return y_coord, x_coord

###################################################################


def main():

    args = parse_args()

    obs_id = args.obs_id
    flux_cal = args.calibrator
    qa_dir = args.path
    base_dir = args.base_dir
    n_threads = args.threads
    subband_step = args.subband_step

    # set output directory
    if qa_dir is None:
        if base_dir is not None:
            qa_dir = get_default_imagepath(obs_id, basedir=base_dir)
        else:
            qa_dir = get_default_imagepath(obs_id)

        # check that path exists
        if not os.path.exists(qa_dir):
            print(
                "Directory {0:s} does not exist and will be created".format(qa_dir))
            os.makedirs(qa_dir)

    data_dir = os.path.dirname(qa_dir).rsplit("qa")[0]

    # check the mode to run the validation
    qa_beamweights_dir = os.path.join(qa_dir, "beamweights")

    # check that this directory exists (just in case)
    if not os.path.exists(qa_beamweights_dir):
        print("Directory {0:s} does not exist and will be created".format(
            qa_beamweights_dir))
        os.makedirs(qa_beamweights_dir)

    lib.setup_logger(
        'debug', logfile='{0:s}/create_beamweights.log'.format(qa_beamweights_dir))
    logger = logging.getLogger(__name__)

    # get a list of beams if no beam was provided
    if args.beam is None:
        data_dir_beam_list = glob.glob(os.path.join(data_dir, "[0-3][0-9]"))
        # check that there are beams
        if len(data_dir_beam_list) == 0:
            logger.warning("No beams found in {}".format(data_dir))
            return None
        else:
            beam_list = [int(os.path.dirname(beam).split("/")[-1])
                         for beam in data_dir_beam_list]
    else:
        beam_list = [args.beam]

    # now go through the beams
    for beam_nr in beam_list:

        # check that the given calibrator exists
        data_cal_dir = os.path.join(data_dir, "{0:02d}".format(beam_nr))

        # calibrator file
        cal_file = os.path.join(data_cal_dir, "raw/{}.MS".format(flux_cal))

        # check that it exists
        if not os.path.exists(cal_file):
            logger.warning(
                "Could not find calibrator {}. Continue with next beam".format(cal_file))
            continue
        else:
            logger.info("Found calibrator {}".format(cal_file))

        # set output directory for plots
        qa_beamweights_beam_dir = os.path.join(
            qa_beamweights_dir, "{0:02d}".format(beam_nr))
        # check that this directory exists (just in case)
        if not os.path.exists(qa_beamweights_beam_dir):
            logger.info("Directory {0:s} does not exist and will be created".format(
                qa_beamweights_beam_dir))
            os.makedirs(qa_beamweights_beam_dir)

        # Start with one measurement set to set up the size of the array
        #
        # cal = pt.table(
        #     "/data/hess/apertif/{}/{}/WSRTA{}_B000.MS/APERTIF_CALIBRATION".format(args.cal_date, args.taskid, args.taskid),
        #     ack=False)
        cal = pt.table(os.path.join(
            cal_file, "APERTIF_CALIBRATION"), ack=False)

        # Set up array for all beams, subbands, antennas
        num_beams = 40
        num_subbands = pt.taql(
            'select distinct SPECTRAL_WINDOW_ID FROM $cal').nrows()
        num_antennas = pt.taql(
            'select distinct ANTENNA_ID FROM $cal').nrows()

        beamweights = np.zeros(
            (num_beams, num_subbands, num_antennas, 11, 11), dtype=np.complex64)

        logger.info("Number of subbands in {0} is {1}".format(
            os.path.basename(cal_file), num_subbands))

        # Old implementation looped over beams (and I just picked a subband for simplicity, but this could be expanded to loop over subbands)
        #
        # plot_sub = 350
        # for beam_nr in range(40):
        #     ms_name = "/data/hess/apertif/{}/{}/WSRTA{}_B0{:02}.MS/APERTIF_CALIBRATION".format(args.cal_date, args.taskid,
        #                                                                                         args.taskid, beam_nr)
        #     print(ms_name)
        #     cal = pt.table(ms_name, ack=False)
        #     weights_gershape = cal.getcol('BEAM_FORMER_WEIGHTS').reshape((num_subbands, -1, 2, 64))
        #
        #     for subband in range(num_subbands):
        #         for antenna in range(num_antennas):
        #             beamweights[beam_nr, subband, antenna] = convert_weights(weights_gershape[subband, antenna])
        #
        #     print("BEAM NUMBER {}".format(beam_nr))
        #     # fig, axs = plt.subplots(3, 4, figsize=(15, 11))
        #     fig, axs = plt.subplots(3, 4, figsize=(10, 7))
        #     fig.suptitle("Beam {}; Subband {}".format(beam_nr, plot_sub), fontsize=14)
        #     for ax, plot_ant in zip(np.array(axs).flatten(), range(num_antennas)):
        #         ax.imshow(np.abs(beamweights[beam_nr, plot_sub, plot_ant]), cmap='plasma')
        #         ax.set_title("Antenna " + str(plot_ant))
        #         if plot_ant < 8:
        #             ax.set_xticklabels([])
        #         for i in range(61):
        #             x, y = give_coord('X', i)
        #             ax.text(x - 0.35, y + 0.18, 'X' + str(i), color='white', fontsize=5)
        #             x, y = give_coord('Y', i)
        #             ax.text(x - 0.35, y + 0.18, 'Y' + str(i), color='white', fontsize=5)
        #
        #     plt.savefig('/data/hess/apertif/{}/{}_B0{:02}_S{:03}_weights.png'.format(args.cal_date, args.cal_date,
        #                                                                              beam_nr, plot_sub))
        #     plt.close()

        # New implementation because I was just thinking of using a single beam and plotting a bunch of subbands. (quick and dirty solution)
        # Beam is chosen by the user and saved in args.beam
        # ms_name = "/home/hess/apertif/{}/{:02}/3C147.MS/APERTIF_CALIBRATION".format(
        #     args.taskid, beam_nr)
        # cal = pt.table(ms_name, ack=False)

        weights_gershape = cal.getcol(
            'BEAM_FORMER_WEIGHTS').reshape((num_subbands, -1, 2, 64))

        # parallelise it to plot faster
        # with pymp.Parallel(n_threads) as p:
        # go throught the subband
        # for subband_index in p.range(len(num_subbands)):
        for subband_index in range(num_subbands):
            # to speed things, every subband_step-th subband can be used
            subband = subband_index * subband_step
            for antenna in range(num_antennas):
                beamweights[beam_nr, subband, antenna] = convert_weights(
                    weights_gershape[subband, antenna])

            fig, axs = plt.subplots(3, 4, figsize=(10, 7))
            fig.suptitle("Beam {}; Subband {}".format(
                beam_nr, subband), fontsize=14)
            for ax, plot_ant in zip(np.array(axs).flatten(), range(num_antennas)):
                ax.imshow(
                    np.abs(beamweights[beam_nr, subband, plot_ant]), cmap='plasma')
                ax.set_title("Antenna " + str(plot_ant))
                if plot_ant < 8:
                    ax.set_xticklabels([])
                for i in range(61):
                    x, y = give_coord('X', i)
                    ax.text(x - 0.35, y + 0.18, 'X' + str(i),
                            color='white', fontsize=5)
                    x, y = give_coord('Y', i)
                    ax.text(x - 0.35, y + 0.18, 'Y' + str(i),
                            color='white', fontsize=5)

            plot_name = os.path.join(qa_beamweights_beam_dir, "{0}_{1}_B{2:02d}_S{3:03d}_weights.png".format(
                obs_id, flux_cal, beam_nr, subband))
            # plt.savefig('/home/hess/apertif/{}/{}_B0{:02}_S{:03}_weights.png'.format(args.taskid, args.cal_date,
            #                                                                          beam_nr, subband))
            plt.savefig(plot_name, overwrite=True)
            plt.close('all')


if __name__ == '__main__':
    main()
