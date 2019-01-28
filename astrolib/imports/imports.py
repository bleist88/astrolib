"""
This file contains all the imports used throughout the astrolib project.  This
is considered bad practice, but boy does it make each file look a lot cleaner.
"""

from    astrolib    import io
from    astrolib    import maths
from    astrolib    import mcc
from    astrolib    import photo

import  os
import  sys
import  shutil
import  time
import  copy
import  pickle
import  gzip
import  pyarrow
import  warnings
warnings.filterwarnings("ignore")

import  numpy as np
import  scipy as sp
np.seterr( all="ignore" )

from    matplotlib              import pyplot
from    matplotlib              import colors
from    matplotlib              import animation
from    mpl_toolkits.mplot3d    import Axes3D

from    astropy.io              import fits
from    astropy.wcs             import WCS

