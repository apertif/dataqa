from merge_ccal_scal_plots import run_merge_plots
import numpy as np
import os

basedir = '/data/apertif/190602049_flag-strategy-test/qa'

do_ccal = True

do_scal = False

# file_list = np.array([os.path.join(basedir, img) for img in img_list])

# new_file_name = os.path.join(basedir, "merge_test.png")

run_merge_plots(basedir, do_ccal=do_ccal, do_scal=do_scal)
