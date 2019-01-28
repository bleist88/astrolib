"""
The module contains correlation functions and routines.
"""

from ._imports import *

##  ============================================================================

def correlate( Ax, Ay, Bx, By, Rc, Rc_min=None, Rc_unit="arcsecs" ):
    """
    This function correlates objects from positions B to positions A using the
    correlation radius Rc.
    """

    ##  Convert Rc units to degrees.

    if Rc_unit in ["arcsecond","arcseconds","arcsec","arcsecs","as"]:
        Rc /= 3600

    ##  Ensure that position arguments are numpy arrays with agreeable lengths.
    ##  Ensure that Rc argument becomes a numpy array.

    Ax, Ay      = np.array( Ax ), np.array( Ay )
    Bx, By      = np.array( Bx ), np.array( By )

    if Ax.size != Ay.size:
        raise TypeError("Ax and Ay must be of the same length.")

    if Bx.size != By.size:
        raise TypeError("Bx and By must be of the same length.")

    if isinstance( Rc, (float, int) ):

        rc  = np.copy( Rc )
        Rc  = np.zeros( Ax.size )
        Rc.fill( rc )

    else:

        try:
            Rc      = np.array( Rc )
        except:
            raise TypeError("Rc must be of type 'float', 'int', or 'array'.")

        if Rc.size != Ax.size:
            raise TypeError(
                "If Rc is an array, it must be the same size as Ax."
            )

    if Rc_min is not None:
        Rc[ np.where( Rc < Rc_min )[0] ]    = Rc_min

    ##  Create arrays to store matching indices from positions b onto a and an
    ##  array to store their separations.

    M, S    = np.zeros(
        Ax.size, dtype='int64' ), np.zeros( Ax.size, dtype='float64'
    )
    M.fill( -99 )
    S.fill( -99 )

    ##  Find a nearest neighbor in positons b for every position a and keep as a
    ##  match if its separation is within the correlation radius.

    for i in range( Ax.size ):

        io.progress( i, Ax.size, alert="Correlating..." )

        Sj      = np.sqrt( (Bx - Ax[i])**2 + (By - Ay[i])**2 )
        M[i]    = np.where( Sj == np.min(Sj) )[0][0]
        S[i]    = Sj[ M[i] ]

    ##  Take the square root of the separations squared.

    far     = np.where( S > Rc )[0]
    M[far]  = -99
    S[far]  = -99

    ##  Return array of matches and separations.
    ##  Return indices of the positively correlated in M.
    ##  Return indices of the negatively correlated in positions b.

    M, S    = clean_duplicates( M, S )
    Pa      = np.where( M >= 0 )[0]
    Nb      = np.delete( np.arange(Bx.size), M[Pa] )

    return  M, S, Pa, Nb

##  ============================================================================

def clean_duplicates( M, S ):
    """
    This function removes duplicate objects from the matches and separations
    arrays.  Of any repeat objects, the one of the smallest separation is the
    one kept while all others are set to -99.
    """

    ## Find duplicated correlated objects.
    ## Keep only the smaller of the separations.

    for i in range( M.size ):

        io.progress( i, M.size, alert='Cleaning...' )

        if M[i] >= 0:

            others  = np.where( M == M[i] )[0]

            if others.size > 1:

                far = others[
                    np.where( S[others] > np.min(S[others]) )[0]
                ]

                M[far]  = -99
                S[far]  = -99

    return M, S

##  ============================================================================

def combine( catalogs, Rc, x_col="alpha", y_col="delta" ):
    """
    This function takes as input a list of catalogs and combine them into a
    single catalog.  This combines them such that all objects in the combined
    catalog are listed only once. All catalogs to be combined must have the same
    column format.

    Parameters:
    *   catalogs    ( list<numpy.ndarrays> )
                    list of file paths to all catalogs to be combined
    *   Rc          ( float, numpy.array\<float> )
                    correlation radius or radii
    *   x_col       ( string )
                    coordinate 1 column name
    *   y_col       ( string )
                    coordinate 2 column name
    """

    ## Initialize combined catalog with the first catalog.

    print( "Combining all catalogs into one using Rc = %.3f..." % Rc )

    combined    = catalogs[0]

    ## Correlate and add catalogs to the combined.

    for i in range( 1, len(catalogs) ):

        print( "    Adding catalog %i to the combined catalog..." % i )

        dat     = catalogs[i]

        M, S, Pa, Nb    = correlate(
            combined[ x_col ], combined[ y_col ],
            dat[ x_col ], dat[ y_col ],
            Rc
        )

        ## Add only objects which were not matched.

        combined    = np.concatenate( ( combined, dat[ Nb ] ), axis=0 )

        print( "    matched objects:    ", Pa.size )
        print( "    new objects:        ", Nb.size )

    print( "    total objects:  ", combined.size )

    ## Return the combined catalog.

    return combined
