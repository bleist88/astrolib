"""
This file contains functions that deal with formatting strings and arrays.
"""

from    __future__  import absolute_import
from    __future__  import division
from    __future__  import print_function
from    __future__  import unicode_literals

from   .__imports__ import *

##  ========================================================================  ##

def get_dstring( dtype, space=3, sci=False, ipad=6, fpad=8.6, spad=32 ):
    """
    This function creates and returns a format string for a single line of a
    numpy style dtype.  There is still a lot of work to do for this!  Currently
    this searches for the following data types:
        U           - string
        S, s        - byte string
        i, int      - integer
        f, float    - float
    Parameters:
        dtype       - dict
            numpy dtype or dtype dictionary
        space       - int
            number of spaces between columns
        sci         - bool
            hack to use scientific notation instead of flaots
        ipad        - int
            format for integers
        fpad        - float
            format for floats
        spad        - int
            format for strings ( currently pretty lame )
    Returns:
        dstring     - string
            format string for one line of an array.
    """

    ## Ensure that the dtype is a numpy dtype.

    dtype   = np.dtype( dtype )

    ## Get Formats.

    dstring     = ''

    for name in list( dtype.names ):

        if 'U' in str( dtype[name] ):

            #spad        = len(max( array[name], key=len ))
            dstring    += space * ' ' + '%-' + str(spad) + 's'

        elif 'S' in str( dtype[name] ):

            #spad        = len(max( array[name], key=len ))
            dstring    += space * ' ' + '%-' + str(spad) + 's'

        elif 's' in str( dtype[name] ):

            #spad        = len(max( array[name], key=len ))
            dstring    += space * ' ' + '%-' + str(spad) + 's'

        elif 'i' in str( dtype[name] ):

            dstring    += space * ' ' + '%' + str(ipad) + 'i'

        elif 'f' in str( dtype[name] ):

            if sci is False:
                dstring    += space * ' ' + '%' + str(fpad) + 'f'
            elif sci is True:
                dstring    += space * ' ' + '%' + str(fpad) + 'f'

    return dstring

##  ========================================================================  ##

def tobool( val ):
    """
    Convert string object to boolean.
    """

    if val.lower() in [ "y", "yes", "t", "true", "1", 1 ]:
        return True

    else:
        return False
