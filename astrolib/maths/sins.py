
from astrolib.imports import *

##  variables

dx      = 0.01
dt      = 0.025

tau     = 0.01
rt      = 3

c       = 3, .51
k       = 1, 20
w       = 1, -3

figsize = 14, 6
x_lims  = 0, 2*np.pi
y_lims  = -4, 4

##  ========================================================================  ##

pyplot.ion()

fig = pyplot.figure( figsize=figsize )
ax1 = pyplot.subplot( 211 )
ax2 = pyplot.subplot( 212 )

##  ========================================================================  ##

x   = np.arange( x_lims[0], x_lims[1] + dx, dx )
t   = 0

while t < rt:

    y1  = c[0] * np.sin( k[0]*np.pi*x - w[0]*np.pi*t )
    y2  = c[1] * np.sin( k[1]*np.pi*x - w[1]*np.pi*t )

    ax1.plot( x, y1 )
    ax1.plot( x, y2)
    ax1.set_xlim( x_lims[0], x_lims[1] )
    ax1.set_ylim( y_lims[0], y_lims[1] )

    ax2.plot( x, y1 + y2 )
    ax2.set_xlim( x_lims[0], x_lims[1] )
    ax2.set_ylim( y_lims[0], y_lims[1] )

    pyplot.pause( tau )
    ax1.clear()
    ax2.clear()

    t += dt
