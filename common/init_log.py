#!/usr/bin/env python3

import os
import logging
import logging.handlers


def init_logging(logfile):
    format = "%(asctime)-15s %(message)s"
    logging.basicConfig(format=format, level=logging.DEBUG)
    root = logging.getLogger('')

    if logfile:
        logfile = os.path.abspath(logfile)
        try:
            os.makedirs(os.path.dirname(logfile))
        except OSError:
            pass

        fh = logging.handlers.RotatingFileHandler(logfile, maxBytes=500000, backupCount=5)
        fh.setFormatter(logging.Formatter(format))
        fh.setLevel(logging.DEBUG)
        root.addHandler(fh)
