
from __imports__ import *

##  ========================================================================  ##
##  User Variables

R               = 2, 3
Ri, Ro          = 6, 10
units           = "arcsecond"

fits_file       = "Data/SUBARU/g_subaru.fits"
scale           = 0.15
seeing          = 0.95
S               = 10

#fits_file       = "Data/GALEX/FUV_galex.fits"
#scale           = 1.5
#seeing          = 5.6
#Ri, Ro          = 10, 18
#S               = 20

mc_file         = "Master/COSMOS.mc"
di              = 3023

##  ========================================================================  ##
##  Script

##  Open mc_file.

print("Opening the MC file...")

MC          = Mc3.Master( mc_file )
Master      = MC.master
N           = MC.N

del MC

##  Create stamp object.

Stamp       = Photometry.Stamp( S, scale, units=units )

##  Setup initial stamp parameters.

Stamp.set_apertures( step=scale )
Stamp.set_annulus( Ri, Ro )
#Stamp.calc_psf( .5 * seeing )

##  For each object specified by di.

print("Looping through selection of objects...")

for i in range( 0, N, di ):

    print( "Object %i" % i )

    alpha   = Master["alpha"][i]
    delta   = Master["delta"][i]

    ##  Setup data.

    image       = fits.open( fits_file )
    Stamp.set_data( image[0].data, image[0].header, alpha=alpha, delta=delta )

    ##  Perform photometry.

    #Stamp.calc_sky( sigma=3, epsilon=.01 )
    Stamp.calc_flux( subtract=False, psf=True )
    Stamp.calc_profile( .5 * seeing )

    ##  Estimate flux at each R.

    for r in R:

        flux    = Stamp.get_flux( r )
        print( "%.2f = %.5f" % (r, flux) )

    ##  Create figure.

    #Stamp.plot_stamp
    Stamp.create_figure( R=R, sigma=2, yscale="linear" )
    pyplot.show()
