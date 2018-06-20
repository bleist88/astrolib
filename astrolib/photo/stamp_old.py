
from .__imports__ import *

################################################################################

arc_units   = [
    "second", "sec", "seconds", "secs",
    "arcsecond", "arcsec", "arcseconds", "arcsecs", "as"
]

deg_units   = [
    "degree", "degrees", "deg", "degs", "d"
]

pix_units   = [
    "pixel", "pixels", "pix", "pixs", "p"
]

def to_pixels( R, pix_scale, unit ):

    if unit in arc_units or unit in deg_units:
        R   = R / pix_scale
    elif unit not in pix_units:
        print("The unit ", unit, " is not recognized.")

    return  R

################################################################################

class Stamp:

    def __init__( self, radius, pix_scale, unit="pixels" ):

        ##  Data Array Parameters

        self.shape      = None      ##  shape of array [pixels]
        self.pix_scale  = None      ##  [unit] / pixel
        self.unit       = None      ##  angle unit

        self.data       = None      ##  data array
        self.grid       = None      ##  meshgrid (X, Y)
        self.map        = None      ##  meshgrid (ALPHA, DELTA)
        self.radial     = None      ##  radial distance array sqrt(X**2 + Y**2)

        self.WCS        = None      ##  world coordinate system of image

        ##  Target Parameters

        self.x          = None      ##  target coordinates [pixels]
        self.y          = None
        self.alpha      = None      ##  target coordinates [unit]
        self.delta      = None
        self.x_c        = None      ##  center pixel coordinates [pixels]
        self.y_c        = None
        self.alpha_c    = None      ##  center pixel coordinates [unit]
        self.delta_c    = None
        self.x_off      = None      ##  offset ( x - x_c )
        self.y_off      = None      ##  offset ( y - y_c )

        ##  Aperture and Photometry Parameters

        self.r          = None      ##  [ aperture radii [pixels], ]
        self.aperture   = None      ##  [ aperture arrays of values 0 and 1, ]
        self.th_area    = None      ##  [ theoretical aperture area [pixels], ]
        self.pix_area   = None      ##  [ true aperture area [pixels], ]

        self.Ri         = None      ##  inner annulus radius [pixels]
        self.Ro         = None      ##  outer annulus radius [pixels]
        self.annulus    = None      ##  array of annulus arrays of values {0,1}
        self.an_area    = None      ##  pixel area of the annulus

        self.flux       = None      ##  array of pure flux values at radius r
        self.profile    = None      ##  derivative of flux:  d(flux)/dr

        self.sky        = None      ##  derived sky background value
        self.sky_std    = None      ##  sky background standard deviation
        self.sky_flux   = None      ##  array of sky flux values at radius r

        self.psf        = None      ##  array of the point spread function
        self.psf_std    = None      ##  standard deviation of the psf
        self.psf_frac   = None      ##  array of psf fraction in aperture

        self.err_php    = None      ##  random noise error
        self.err_sky    = None      ##  uncertainty in the sky mean
        self.err_std    = None      ##  random sky fluctuations
        self.err_flux   = None      ##  net flux error
        self.err_mag    = None      ##  net flux magnitude error

        ##  Initialize data members.

        radius          = to_pixels( radius, pix_scale, unit )
        self.unit       = unit

        self.shape      = int(2 * radius + 1), int(2 * radius + 1)
        self.pix_scale  = pix_scale

        self.x_c        = int( self.shape[0] / 2 )
        self.y_c        = int( self.shape[1] / 2 )

        self.data       = np.zeros( self.shape )
        self.grid       = np.meshgrid(
            np.arange( self.shape[0] ), np.arange( self.shape[1] )
        )
        self.radial     = np.sqrt(
            (self.grid[0] - self.x_c)**2 + (self.grid[1] - self.y_c)**2
        )

        ##  Initialize photometry members.

        self.annulus    = np.ones( self.shape )
        self.sky        = 0.0
        self.sky_std    = 0.0
        self.frac       = 1.0

    ##  ====================================================================  ##
    ##  Data Manipulation

    def set_data( self, image, header, alpha=None, delta=None, x=None, y=None ):

        ## Get image data and wcs info.

        self.WCS    = WCS( header )

        ##  Retrieve alternate coordinates (alpha, delta) <--> (x, y).

        if alpha is not None and delta is not None:

            position    = np.array([[ alpha, delta ]])
            im_x        = self.WCS.wcs_world2pix( position, 1 )[0][1]
            im_y        = self.WCS.wcs_world2pix( position, 1 )[0][0]
            im_x0       = int( im_x )
            im_y0       = int( im_y )
            self.alpha  = alpha
            self.delta  = delta
            self.x_off  = im_x - ( im_x0 + 0.5 )
            self.y_off  = im_y - ( im_y0 + 0.5 )

        elif x is not None and y is not None:

            position    = np.array([[ x, y ]])
            im_x        = x
            im_y        = y
            im_x0       = int( im_x )
            im_y0       = int( im_y )
            self.alpha  = self.WCS.wcs_pix2world( position, 1 )[0][0]
            self.delta  = self.WCS.wcs_pix2world( position, 1 )[0][1]
            self.x_off  = im_x - ( im_x0 + 0.5 )
            self.y_off  = im_y - ( im_y0 + 0.5 )

        else:

            raise   Exception(
                "Both 'alpha' and 'delta' must be supplied or both 'x' and 'y'"\
                "must be supplied."
            )

        ##  Rotate the stamp so that North is up.
        ##  Determine Rotation factor (rotate in k factors of pi/2).
        ##  Get the delta of the pixels around the center.

        around      = np.array([
            [ im_x0,       im_y0 + 1  ],
            [ im_x0 + 1,   im_y0      ],
            [ im_x0,       im_y0 - 1  ],
            [ im_x0 - 1,   im_y0      ]
        ])

        positions   = self.WCS.wcs_pix2world( around, 1 )

        if (positions[1][1] - positions[3][1]) > 0:
            k  = 3
        elif (positions[1][1] - positions[3][1]) > 0:
            k  = 2
        elif (positions[1][1] - positions[3][1]) > 0:
            k  = 1
        else:
            k  = 0

        ##  Set using the grid method.
        ##  Use "try:" in order to troubleshoot stamp exceeding the image.

        try:
            self.data[self.grid]    = image[
                self.grid[0] + im_x0 - self.x_c,
                self.grid[1] + im_y0 - self.y_c
            ]
            self.data               = np.rot90( self.data, k=k )
            self.data              -= np.min( self.data )

        except:
            self.data[self.grid]    = 0.0

    ##  ====================================================================  ##
    ##  Aperture Manipulation

    def set_apertures( self, dr=1 ):

        ##  Create array of apertures for each radius in r.
        ##  The extra "1e-8" term is just a temporary bug fix.

        dr          = to_pixels( dr, self.pix_scale, self.unit )
        self.r      = np.arange( 0, self.x_c, dr )

        ##  Initialize all arrays which relate to r.

        self.flux       = 0 * self.r
        self.profile    = 0 * self.r
        self.pix_area   = 0 * self.r
        self.area       = np.pi * self.r**2

        self.aperture   = []
        self.pix_area   = 0 * self.r

        for i, r in enumerate( self.r ):

            aperture    = np.zeros( self.shape, dtype="int32" ) + 1
            annulus     = np.zeros( self.shape, dtype="int32" ) + 1

            aperture[ np.where( self.radial > r + 1e-8 ) ]  = 0
            self.aperture.append( aperture )
            self.pix_area[i]    = np.sum( aperture )

        self.aperture   = np.array( self.aperture )

    def set_annulus( self, Ri, Ro ):

        self.Ri     = to_pixels( Ri, self.pix_scale, self.unit )
        self.Ro     = to_pixels( Ro, self.pix_scale, self.unit )

        self.annulus    = np.zeros( self.shape, dtype="int32" ) + 1

        self.annulus[
            np.where(
                (self.radial < self.Ri) | (self.radial > self.Ro)
            )
        ]   = 0

    def find_R( self, R ):

        ##  Find and return the i^th position of r in which r[i] < R < r[i+1].

        j   = 0

        for i in range( self.r.size - 1 ):
            if self.r[i] <= R and R <= self.r[i+1]:
                j   = i

        return  j

    def set_psf( self, std ):

        self.psf_std    = to_pixels( std, self.pix_scale, self.unit )
        self.psf        = np.exp( -.5 * (self.radial / std)**2 )
        self.psf_frac   = 0 * self.r

        for i in range( self.r.size ):
            self.psf_frac[i]    = np.sum( self.apertures[i] * self.psf )

        self.psf_frac  /= np.sum( self.psf )

    ##  ========================================================================
    ##  Photometry

    def calc_sky( self, sigma=3, epsilon=.03, iters=20 ):

        ##  Iteratively remove outliers and calculate statistics.

        sky_data    = self.data[ np.where( self.annulus > 0 ) ]

        while True:

            iters      -= 1

            mean0       = np.mean( sky_data )
            std         = np.std( sky_data )
            sky_data    = sky_data[ np.where( sky_data < mean0 + sigma * std ) ]

            ##  Use SExtractor's background calculation.

            self.sky        = 2.5*np.median(sky_data) - 1.5*np.mean(sky_data)
            self.sky_std    = std

            if np.abs( mean0 - self.sky ) / mean0 < epsilon or iters <= 0:
                break

    def calc_flux( self, subtract=False, psf=False ):

        ##  Calculate basic flux.

        for i in range( self.r.size ):
            self.flux[i]    = np.sum( self.aperture[i] * self.data )

        self.flux      *= self.area / self.pix_area

        ##  Subtract the sky from the flux profile.
        ##  Correct for psf.

        if subtract is True:
            self.flux  -= self.sky * self.area

        if psf is True:
            self.flux  /= self.frac

        ##  Calculate the profile ( d(flux)/dr ) of the flux.

        self.profile[1:-1]  = (self.flux[1:-1] - self.flux[:-2])
        self.profile[1:-1] /= (self.r[1:-1] - self.r[0:-2])
        self.profile[-1]    = self.profile[-2]

    def smooth_flux( self, std ):

        std     = to_pixels( std, self.pix_scale, self.unit )

        flux    = np.zeros( self.flux.size )

        for i in range( 1, self.r.size - 1 ):

            weights = np.exp( -.5 * ((self.r - self.r[i]) / std)**2 )
            flux[i] = np.average( self.flux, weights=weights )

        self.flux   = flux

        ##  Calculate the slope ( d(flux)/dr ) of the flux.

        self.profile[1:-1]  = (self.flux[1:-1] - self.flux[:-2])
        self.profile[1:-1] /= (self.r[1:-1] - self.r[0:-2])
        self.profile[-1]    = self.profile[-2]

    def get_flux( self, R ):

        ##  Estimate the flux at the specifed radius by linear interpolation.

        i       = self.find_R( R )
        dR      = R - self.r[i]

        return  self.flux[i] + (dR * self.profile[i+1])

    def calc_errors( self ):

        ##  error1[g] = area[g]*skyvar          ;;  scatter in sky values
        ##  magerr[g] = sqrt(error1[g] + error2[g] + error3[g])

        ##  error2[g] = (apmag[g] > 0)/phpadu   ;;  random photon noise
        self.err_php    = self.flux / self.php  ##  random noise error

        ##  error3[g] = sigsq*area[g]^2         ;;  uncertainty in mean sky
        self.err_sky    = self.ap_area**2 * self.sky_std**2 / self.an_area      ##  uncertainty in the sky mean


        self.err_std    = None      ##  random sky fluctuations
        self.err_flux   = None      ##  net flux error
        self.err_mag    = None      ##  net flux magnitude error

    ##  ====================================================================  ##
    ##  Plotting

    def plot_stamp( self,
        axes, R=None, annulus=True, sigma=3, epsilon=0.03,
        cmap="gray", color="y", unit="pixels"
    ):

        axes.imshow(
            photo.rescale( self.data, sigma=sigma, epsilon=epsilon ),
            cmap=cmap
        )

        ##  Draw apertures.

        if R is not None:

            if isinstance( R, (int,float) ):
                R   = [ to_pixels(R, self.pix_scale, self.unit) ]

            else:
                for i in range(len(R)):
                    R[i] = to_pixels(R, self.pix_scale, self.unit)

            for r in R:

                axes.add_artist(
                    pyplot.Circle(
                        (self.x_c, self.y_c), radius=r,
                        color=color, lw=2, fill=False
                    )
                )

        ##  Draw annulus.

        if annulus is True and self.annulus is not None:

            axes.add_artist(
                pyplot.Circle(
                    (self.x_c, self.y_c), radius=self.Ri,
                    color=color, linestyle="--", lw=2, fill=False
                )
            )

            axes.add_artist(
                pyplot.Circle(
                    (self.x_c, self.y_c), radius=self.Ro,
                    color=color, linestyle="--", lw=2, fill=False
                )
            )

    def plot_flux( self, axes, R=None, annulus=True, yscale="log" ):

        axes.set_ylim( 0, 1.1 )

        flux        = self.flux / np.max(self.flux)
        slope       = self.profile / np.max(self.profile)
        area        = self.area / self.pix_area

        ##  Plot the basic flux profile.

        axes.plot( self.r,  flux,        "k"    )
        axes.plot( self.r,  slope,       "c-"   )
        axes.plot( self.r,  area,        "r--"  )

        ##  Plot aperture lines.

        if R is not None:

            if isinstance( R, (int,float) ):
                R   = [ to_pixels(R, self.pix_scale, self.unit) ]

            else:
                for i in range(len(R)):
                    R[i] = to_pixels(R, self.pix_scale, self.unit)

            for r in R:

                flux    = self.get_flux( r ) / np.max( self.flux )
                axes.plot( [r, r], [0, flux], "y" )

        ##  Plot the annulus.

        if annulus is True:

            flux    = self.get_flux( self.Ri ) / np.max( self.flux )
            axes.plot( [self.Ri, self.Ri], [0, flux], "y--" )

            flux    = self.get_flux( self.Ro ) / np.max( self.flux )
            axes.plot( [self.Ro, self.Ro], [0, flux], "y--" )

        ##  Set the scaling.

        try:
            axes.set_yscale( yscale )
        except:
            pass

    def create_figure( self, R=None, sigma=3, epsilon=0.03, yscale="log", saveas=False ):

        Fig     = pyplot.figure( figsize=(14,6) )
        Ax1     = Fig.add_subplot( 1,2,1 )
        Ax2     = Fig.add_subplot( 1,2,2 )

        Ax1.set_xlabel("x [pixel]")
        Ax1.set_ylabel("y [pixel]")

        Ax2.set_xlabel("Aperture [pixel]")
        Ax2.set_ylabel("Flux [normalized]")

        self.plot_stamp( Ax1, R=R, sigma=sigma, epsilon=epsilon )
        self.plot_flux( Ax2, R=R, yscale=yscale )

        if saveas is False:
            pyplot.show()
        else:
            try:    ##  This is because of more problems with the log scale.
                pyplot.savefig( saveas )
            except:
                pass
