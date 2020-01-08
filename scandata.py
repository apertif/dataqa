import os
import numpy as np
import logging


def get_default_imagepath(scan, basedir=None):
    """
    Get the default path for saving images

    | Args:
    |     scan (int): scan (or task id), e.g. 190303084
    |     basedir (str): based directory of the scan, default /data/apertif/

    Returns:
        str: Path for storing images
    """
    if basedir is not None:
        return os.path.join(basedir, '{scan}/qa/'.format(scan=scan))
    else:
        return '/data/apertif/{scan}/qa/'.format(scan=scan)


class ScanData(object):
    """
    Define object classes for holding data related to scans
    The key thing to specify an object is the scan of the target field
    Also need name of fluxcal (for cross-cal solutions)
    Want to add functionality for pol-cal for pol solutions (secondary)
    This specifies the location of all data, assuming setup of automatic pipeline
    (/data/apertif, distributed across happili nodes)
    """

    def __init__(self, scan, sourcename, basedir=None, trigger_mode=False):
        """
        Initialize with scan (taskid) and source name
        and place holders for phase and amplitude

        | Args:
        |     scan (int): scan number, e.g. 190303083
        |     sourcename (str): name of source, e.g. "3C48"
        """
        self.scan = scan
        self.sourcename = sourcename
        self.imagepathsuffix = ""
        self.trigger_mode = trigger_mode
        # check if fluxcal is given as 3CXXX.MS or 3CXXX
        # Fix to not include .MS no matter what
        if self.sourcename[0:2] != '3C':
            logging.warning("Fluxcal doesnt' start with 3C - are you sure?")
        elif self.sourcename[-2:] == 'MS':
            self.sourcename = self.sourcename[:-3]
        # also get a directory list and beamlist
        self.dirlist = []
        self.beamlist = []
        # first check what happili node on
        # if not happili-01, print a warning and only search locally
        hostname = os.uname()[1]
        paths = []
        # in case it runs on triggered mode, it should only look into
        # the apertif dir of this node
        if self.trigger_mode:
            logging.info(
                "--> Running in trigger mode. Looking only for data processed by Apercal on {0:s} <--".format(hostname))
            path = '/data/apertif/{}'.format(self.scan)
            paths = [path]
        elif hostname != 'happili-01' and not trigger_mode:
            logging.info(
                'Not on happili-01, only search local {} for data'.format(hostname))
            if basedir is not None:
                path = os.path.join(basedir, "{}".format(self.scan))
            else:
                path = '/data/apertif/{}'.format(self.scan)
            paths = [path]
        elif hostname == 'happili-01' and basedir is not None:
            path = os.path.join(basedir, "{}".format(self.scan))
            paths = [path]
        else:
            # On happili-01, so search all nodes
            # ignoring happili-05 - may have to fix this eventually
            logging.info(
                "Running on {0:s}. Search for data from all nodes".format(hostname))
            paths += ['/data/apertif/{}'.format(self.scan)]
            paths += ['/data2/apertif/{}'.format(self.scan)]
            paths += ['/data3/apertif/{}'.format(self.scan)]
            paths += ['/data4/apertif/{}'.format(self.scan)]

        for path in paths:
            allfiles = os.listdir(path)
            for f in allfiles:
                full_path = os.path.join(path, f)
                if os.path.isdir(full_path) and len(f) == 2 and unicode(f, 'utf-8').isnumeric():
                    self.dirlist.append(full_path)
                    # create a list of all directories with full path.
                    # This should be all beams - there should be no other directories
                    # f is a string, so add to beam list to also track info about beams
                    self.beamlist.append(f)

        # Initialize phase & amp arrays - common to all types of
        self.phase = np.empty(len(self.dirlist), dtype=np.ndarray)
        self.amp = np.empty(len(self.dirlist), dtype=np.ndarray)

    def get_default_imagepath(self, scan):
        """
        Wrapper around get_default_imagepath, this can be overridden in scal, ccal with a suffix
        """
        return os.path.join(get_default_imagepath(scan), self.imagepathsuffix)

    def create_imagepath(self, imagepath):
        """
        Create the image path. If imagepath is None, return a default one (and create it).

        Args:
            imagepath (str): path where images should be stored (e.g. "/data/dijkema/190303084" or None)

        Returns:
            str: image path that was created. Will be equal to input imagepath, or a generated path
        """
        if not imagepath:
            imagepath = self.get_default_imagepath(self.scan)

        if not os.path.exists(imagepath):
            logging.info("{} doesn't exist, creating".format(imagepath))
            os.makedirs(imagepath)

        return imagepath
