
from .__imports__ import *
import numpy
from .Mock import mock, mock_true

################################################################################

photo_dtype = {
    "names":    [
        "id", "alpha", "delta"
    ],
    "formats":  [
        "int32", "float64", "float64"
    ]
}

################################################################################

from .__imports__ import *
import numpy

################################################################################

photo_dtype = {
    "names":    [
        "id", "alpha", "delta"
    ],
    "formats":  [
        "int32", "float64", "float64"
    ]
}

################################################################################

def photo_run(
    image_file=None,
    in_file=None,
    out_file=None,
    aperture=None,
    annulus=None,
    stamp_rad=None,
    mag_zero=None,
    dzero=0.0,
    gain=1e10,
    scale=None,
    seeing=None,
    units=None,
    checks=False
):

    print()
    print("Aperture Photometry:")
    print(
        "Reading in FITS image data and initializing stamp object...",
        end="\r"
    )

    ##  Open image and input file.

    image       = fits.open( image_file )[0].data
    header      = fits.open( image_file )[0].header
    positions   = Io.read( in_file )

    ##  Prepare aperture and annulus radii.

    R   = []
    Ri  = annulus[0]
    Ro  = annulus[1]

    if isinstance( aperture, (list,tuple) ):
        for i in range( len(aperture) ):
            R.append( aperture[i] )

    else:
        R.append( aperture )

    ##  Prepare output catalog dtype.
    ##  Add flux, magnitude, and error columns to the dtype for each ap.

    photo_dtype["names"].append( "sky" )
    photo_dtype["names"].append( "sky_std" )
    photo_dtype["formats"].append( "float64" )
    photo_dtype["formats"].append( "float64" )

    for i in range( len(R) ):

        photo_dtype["names"].append( "flux_"    + str(R[i]) )
        photo_dtype["names"].append( "dflux_"   + str(R[i]) )
        photo_dtype["names"].append( "mag_"     + str(R[i]) )
        photo_dtype["names"].append( "dmag_"    + str(R[i]) )

        photo_dtype["formats"].append( "float64" )
        photo_dtype["formats"].append( "float64" )
        photo_dtype["formats"].append( "float64" )
        photo_dtype["formats"].append( "float64" )
        photo_dtype["formats"].append( "float64" )

    photometry          = np.zeros( positions.size, dtype=photo_dtype )
    photometry["id"]    = positions["mid"]
    photometry["alpha"] = positions["alpha"]
    photometry["delta"] = positions["delta"]

    ##  Initialize the output file stream.
    ##  Delete input file.

    init_dat            = np.zeros( 0, dtype=photometry.dtype )
    out_file, dstring   = Io.write( out_file, init_dat, keep=True )

    del positions, init_dat

    ##  Prepare stamp object.

    stamp   = Photometry.Stamp( stamp_rad, scale, units=units )

    stamp.set_apertures( step=scale )
    stamp.set_annulus( Ri, Ro )
    stamp.calc_psf( seeing )

    ##  For each position, set the data and calculate the light profile.

    print()
    print( "Performing aperture photometry on %i apertures..." % len(R) )

    for i in range( photometry.size ):

        Io.progress( i, photometry.size, step=100 )

        ##  Set data and make calculations.

        stamp.set_data(
            image, header,
            alpha=photometry[i]["alpha"],
            delta=photometry[i]["delta"]
        )

        ##  Create sky calculations.

        stamp.calc_sky( sigma=3, epsilon=.01 )
        stamp.calc_flux( subtract=True, psf=True )
        #stamp.calc_profile( .5 * seeing )
        #stamp.calc_slope()

        photometry[i][ "sky" ]      = stamp.sky
        photometry[i][ "sky_std" ]  = stamp.sky_std

        ##  For each aperture, estimate the flux for that aperture.

        for j in range( len(R) ):

            ##  Calculate flux, magnitudes and errors.

            flux    = stamp.get_flux( R[j] )
            mag     = mag_zero - 2.5 * np.log10( flux )

            dflux   = 1.0857 * np.sqrt( stamp.sky**2 * np.pi * R[j]**2 + flux / gain )
            dflux  /= flux
            dmag    = np.sqrt( dflux**2 + dzero**2 )

            ##  Write to the data array.

            photometry[i][ "flux_"      + str(R[j]) ]   = flux
            photometry[i][ "dflux_"     + str(R[j]) ]   = dflux
            photometry[i][ "mag_"       + str(R[j]) ]   = mag
            photometry[i][ "dmag_"      + str(R[j]) ]   = dmag

        ##  Create check images.

        if checks is not False:

            saveas  = "Checks/"
            saveas += Io.parse_path(image_file)[1]
            saveas += "_" + str( photometry["id"][i] ) + ".png"

            if i % checks == 0:

                stamp.calc_profile( .5 * seeing )
                stamp.create_figure( R=R, sigma=2, saveas=saveas, yscale="linear" )

        ##  Write the data to the out_file.

        Io.writeto( out_file, dstring, photometry[i] )

    ##  Exit.

    print("Finished!")
    print()
