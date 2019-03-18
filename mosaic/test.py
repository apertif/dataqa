# coding: utf-8
from pybdsf_mosaic import qa_mosaic_plot_pybdsf_images
import glob
files = glob.glob("/mnt/data/Projects/APERTIF/pipeline/190303087/qa_science_demo_2019/mosaic/pybdsf/*pybdsf_*.fits")
qa_mosaic_plot_pybdsf_images(files)
