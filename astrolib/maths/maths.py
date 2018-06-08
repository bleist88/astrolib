
import numpy as np
import matplotlib.pyplot as pyplot

##  ========================================================================  ##

def factorial( n ):

    N       = np.arange( 1, n+1 )
    fact    = 1

    for i in range( N.size ):

        fact   *= N[i]

    return  fact

##  ========================================================================  ##

def clean_sample( sample, sigma, epsilon, iters=20 ):

    while True:

        ##  Stop when iters reaches 0.

        if iters <= 0:
            break

        iters  -= 1

        ##  Calculate outliers.

        mean        = np.mean( sample )
        std         = np.std( sample )

        outliers    = np.where(
            (sample     > mean + sigma * std) |
            (sample     < mean - sigma * std)
        )[0]

        ##  Break if the mean fraction changed more than epsilon.

        new_mean    = np.mean( sample[outliers] )

        if np.abs( (new_mean - mean) / mean ) < epsilon:
            break

    ##  Return the sample of inliers and outliers.

    inliers     = np.where(
        (sample    <= mean + sigma * std) &
        (sample    >= mean - sigma * std)
    )[0]

    outliers    = np.where(
        (sample     > mean + sigma * std) |
        (sample     < mean - sigma * std)
    )[0]

    return  inliers, outliers

##  ========================================================================  ##

def hist( sample, dx=None, bins=None, min=None, max=None ):

    ##  Use the arguments to define the space.

    x_min   = min
    x_max   = max

    if x_min is None:
        x_min   = np.min( sample )

    if x_max is None:
        x_max   = np.max( sample )

    if dx is None and bins is not None:
        dx  = (x_max - x_min) / bins

    if dx is None and bins is None:
        dx  = .1 * np.std( sample )

    ##  Create arrays.

    x   = np.arange( x_min, x_max + dx, dx )
    N   = np.zeros( x.size, dtype="int64" )

    ##  Count the number of sample points in each bin.

    for i in range( x.size - 1 ):

        N[i]    = np.where(
            (sample >= x[i]) & (sample <= x[i+1])
        )[0].size

    return  x, N

##  ========================================================================  ##

def smooth( x, y, std ):

    Y       = np.copy( y )

    for i in range( 1, x.size-1 ):

        weights = np.exp( -.5 * ((x - x[i]) / std)**2 )
        Y[i] = np.average( y, weights=weights )

    return  Y

##  ========================================================================  ##

def derivative( x, y ):

    d       = np.zeros( y.size )

    d[1:]   = (y[1:] - y[:-1]) / (x[1:] - x[:-1])
    d[0]    = d[1] + (x[1] - x[0]) * (d[2] - d[1])/(x[2] - x[1])

    d[1]    = (.75*d[1] + .25*d[0])
    d[0]    = (.75*d[0] + .25*d[1])

    return  d

##  ========================================================================  ##

def interpolate( x, y, X=None, dx=None, std=None ):

    ##  Smooth the function if std is not None.

    if std is not None:
        y   = smooth( x, y, std )

    ##  Create X array if given dx.

    if X is None and dx is not None:
        X   = np.arange( np.min(x), np.max(x) + dx, dx )

    ##  Create Y array.

    Y   = np.zeros( X.size )

    ##  Calculate the derivative.

    d   = derivative( x, y )
    D   = derivative( x, d )

    ##  Loop through all X points.

    for i in range( 1, X.size ):
        for j in range( x.size - 1 ):
            if X[i] >= x[j] and X[i] < x[j+1]:

                ##  Create gaussian weights to average slope.

                d1      = X[i] - x[j]
                d2      = x[j+1] - X[i]
                S       = (d2 * d[j] + d1 * d[j+1]) / ( d1 + d2 )

                ##  Estimate the point based on the slopes.

                Y[i]    = y[j] + S * d1

    ##  Estimate endpoints.

    Y[0]    = Y[0]
    Y[-1]   = Y[-2]

    return  X, Y

##  ========================================================================  ##

def convolve( x, y, F ):

    ##  Create a longer y so that F can completely pass through.
    ##  Y outside of y is set to 0.

    Y   = np.zeros( y.size + 2 * F.size )
    C   = np.zeros( y.size + 2 * F.size )
    Y[ F.size : F.size + y.size ]   = y

    ##  Convolve F with Y.

    for i in range( C.size - F.size + 1 ):

        C[i]    = np.sum( F * Y[ i : F.size + i ] )

    C   = C[ F.size : F.size + y.size ]

    return  C

##  ========================================================================  ##

def fold( x1, y1, x2, y2, X=None ):

    ##  Use the SED space if X is not specified.

    if X is None:
        X   = x1

    ##  Ensure that the SED and filter are on the same space.

    X, Y1   = interpolate( x1, y1, X=X )
    X, Y2   = interpolate( x2, y2, X=X )

    ##  Integrate the Filter with the SED to obtain the flux.

    flux        = np.trapz( Y1 * Y2, x=X )

    return  flux

##  ========================================================================  ##

def cdf( x, y ):

    Y   = np.zeros( y.size )

    for i in range( x.size ):

        Y[i]    = np.trapz( y[:i], x=x[:i] )

    return  Y
