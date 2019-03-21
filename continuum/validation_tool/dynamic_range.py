#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 14:09:37 2019

@author: AK
"""

import pandas as pd
import astropy.io.fits as fits
import astropy.units as u
from astropy.coordinates import SkyCoord, Angle
from astropy.wcs import WCS

import numpy as np
import matplotlib.pyplot as plt


def get_image_center_beam(image):
    fts = fts = fits.open(image)[0]
    center = SkyCoord(ra=fts.header['CRVAL1'], dec=fts.header['CRVAL2'], unit='deg,deg')
# TODO: is the BPA in degrees?
    beam = Angle([fts.header['BMAJ'], fts.header['BMIN'], fts.header['BPA']], unit=u.deg)
    return center, beam


def sources_within_radius(pybdsfcat, image, radius=30):
    """
    The DataFarame of sources within the given radius (arcmin) from the image center
    based on pybdsf catalog
    """
    a = pd.read_csv(pybdsfcat, skip_blank_lines=True, skiprows=5, skipinitialspace=True)
    center, _ = get_image_center_beam(image)
    coords = SkyCoord(ra=a.RA, dec=a.DEC, unit='deg')
    seps = center.separation(coords).to('arcmin')
    a['Center_sep'] = seps
    res = a.query('@seps < @radius')
    return res


def source_dynamic_range(pybdsfcat, image, radius=30):
    """
    Get the highest dynamic range for sources within 1/4 beam radius
    based on pybdsf catalog (Peak_flux / Resid_Isl_rms)
    """
    d = sources_within_radius(pybdsfcat, image, radius=radius)

# take 10 brightest sources:
    d = d.sort_values('Peak_flux', ascending=False)[:5]

    dr = d.Peak_flux/d.Resid_Isl_rms
    return dr.min(), dr.max()


def local_dynamic_range(pybdsfcat, resimage, radius=30, box=50):
    """
    Get the highest peak-to-artefact ratio in box of +-@box pixels
    for sources within the @radius of the center
    based on pybdsf catalog and residual image
    """
    d = sources_within_radius(pybdsfcat, resimage, radius=radius)

# take 10 brightest sources:
    d = d.sort_values('Peak_flux', ascending=False)[:5]

    center, beam = get_image_center_beam(resimage)
    fts = fits.open(resimage)[0]
    data = fts.data
    wcs = WCS(fts.header).celestial
    data = data[0,0,:,:]
    res = []
    for ra, dec, peak in zip(d.RA, d.DEC, d.Peak_flux):
        pxra, pxdec = wcs.wcs_world2pix([[ra, dec]], 1)[0]
        boxdata = data[int(pxdec-box):int(pxdec+box), int(pxra-box):int(pxra+box)]
        res.append(peak/np.max(abs(boxdata)))
    return min(res), max(res)


if __name__ ==  "__main__":
    cat = '/home/kutkin/tmp/tmp_validation/image_mf_00_pybdsf_comp.csv'
    resimage = '/home/kutkin/tmp/tmp_validation/image_mf_00_pybdsf_gaus_resid.fits'

    dr1 = source_dynamic_range(cat, resimage)

    print dr1

    dr2 = local_dynamic_range(cat, resimage)
    print dr2

    # d.hist(range=[0,500], bins=30)
