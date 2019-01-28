
from ._imports import *

##  ============================================================================

def same_grid( X, x_seds, y_seds, std=None ):
    """
    Place all xs and ys on the same grid X.
    """

    ##  Get all SEDs and filters on the same grid.

    Ys  = []

    for i in range( len(x_seds) ):

        Ys.append( maths.interpolate( x_seds[i], y_seds[j], X=X, std=std )[1] )

    ##  Return the new grid and each new SED.

    return  X, Ys

##  ============================================================================

def mock_photometry( x, y_sed, y_filter, mag_0=30.0 ):
    """
    Return the mock flux and magnitude of each object.  The y_sed and y_filter
    arrays must be on the same grid x.
    """

    flux    = maths.fold( x, y_filter * y_sed )
    mag     = -2.5 * np.log10( flux ) + mag_0

    return  flux, mag

##  ============================================================================

def colors( names, m ):
    """
    Return an antisymmetric matrix of colors c in which c[i,j] = m[i] - m[j].
    """

    ##  Create the matrix.
    ##  Create the index dictionary.

    c   = np.zeros( (len(names), len(names)) )

    I   = {}
    for i, name in enumerate( filter_names ):
        I[ name ]   = i

    ##  Get mock photometry for each filter and sed.

    for i range( len(m) ):
        for j in range( len(m) ):
            c[i,j]  = m[i] - m[j]

    ##  Return.

    return  c
