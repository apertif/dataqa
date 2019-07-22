"""
Script to test plotting images
"""

import numpy
import os
import argparse
from astropy.io import fits
import matplotlib.pyplot as plt
import matplotlib.colors as mc
from astropy.wcs import WCS
import qa_continuum


def main():
    start_time = time.time()

    # Create and parse argument list
    # ++++++++++++++++++++++++++++++
    parser = argparse.ArgumentParser(
        description='Create overview for QA')

    # Input path to fits file
    parser.add_argument("fits_file", type=str,
                        help='Input path to fits file')

    parser.add_argument("--output_file", type=str, default='',
                        help='Output path to fits file. Default current working directory')

    parser.add_argument("--vmin", type=float, default=0.05,
                        help='Min for logscale')

    parser.add_argument("--vmax", type=float, default=1000.,
                        help='Min for logscale')

    args = parser.parse_args()

    fits_file = args.fits_file

    if args.output_file == '':
        output_file = os.path.basename(fits_file).replace(
            ".fits", "{0:.2f}_{1:.0f}.png".format(args.vmin, args.vmax))
    else:
        output_file = args.output

    # get hdus
    fits_hdulist = fits.open(fits_file)

    # get WCS header of cube
    wcs = WCS(fits_hdulist[0].header)

    # remove unnecessary axis
    if wcs.naxis == 4:
        wcs = wcs.dropaxis(3)
        wcs = wcs.dropaxis(2)
        img = fits_hdulist[0].data[0][0]
    elif wcs.naxis == 3:
        wcs = wcs.dropaxis(2)
        img = fits_hdulist[0].data[0]
    else:
        img = fits_hdulist[0].data

    # set up plot
    ax = plt.subplot(projection=wcs)

    # fig = ax.imshow(
    #     img * 1.e3, norm=mc.SymLogNorm(0.2),  origin='lower')

    fig = ax.imshow(
        img * 1.e3, norm=mc.LogNorm(vmin=args.vmin, vmax=args.vmax),  origin='lower')

    cbar = plt.colorbar(fig)
    cbar.set_label('Flux Density [mJy/beam]')

    # legend
    ax.coords[0].set_axislabel('Right Ascension')
    ax.coords[1].set_axislabel('Declination')
    ax.coords[0].set_major_formatter('hh:mm')

    ax.set_title("{0:s}".format(output_file.replace(".png", "")))

    plt.savefig(output, overwrite=True, bbox_inches='tight', dpi=300)
