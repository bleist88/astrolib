
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

def to_pixels( R, scale, units ):

    if units in arc_units or units in deg_units:
        R   = R / scale
    elif units not in pix_units:
        print("The units ", units, " is not recognized.")

    return  R

################################################################################

class Stamp:

    def __init__( self, radius, scale, units="pixels" ):

        ##  Data Array Parameters

        self.shape      = None      ##  shape of array [pixels]
        self.scale      = None      ##  [units] / pixel
        self.units      = None      ##  angle units

        self.data       = None      ##  data array
        self.grid       = None      ##  meshgrid (X, Y)
        self.map        = None      ##  meshgrid (ALPHA, DELTA)
        self.radial     = None      ##  radial distance array sqrt(X**2 + Y**2)

        self.WCS        = None      ##  world coordinate system of image

        ##  Target Parameters

        self.pix_x      = None      ##  center pixel coordinates [pixels]
        self.pix_y      = None
        self.pix_alpha  = None      ##  center pixel coordinates [units]
        self.pix_delta  = None
        self.x          = None      ##  target coordinates [pixels]
        self.y          = None
        self.alpha      = None      ##  target coordinates [units]
        self.delta      = None
        self.dx         = None      ##  offset ( x - pix_x )
        self.dy         = None      ##  offset ( y - pix_y )

        ##  Aperture and Photometry Parameters

        self.r          = None      ##  array of aperture radii [pixels]
        self.aperture   = None      ##  array of aperture arrays of values {0,1}
        self.area       = None      ##  array of desired aperture area [pixels]
        self.pix_area   = None      ##  array of true aperture area [pixels]

        self.Ri         = None      ##  inner annulus radius [pixels]
        self.Ro         = None      ##  outer annulus radius [pixels]
        self.annulus    = None      ##  array of annulus arrays of values {0,1}

        self.flux       = None      ##  array of pure flux values at radius r
        self.profile    = None      ##  array of gaussian smoothed flux
        self.slope      = None      ##  derivative of flux:  d(flux)/dr
        self.curvature  = None      ##  second derivative of flux:  d2(flux)/dr2
        self.sky        = None      ##  derived sky background value
        self.sky_std    = None      ##  sky background standard deviation
        self.sky_flux   = None      ##  array of sky flux values at radius r
        self.psf        = None      ##  array of the point spread function
        self.frac       = None      ##  array of psf fraction in aperture

        ##  Initialize data members.

        radius          = to_pixels( radius, scale, units )
        self.units      = units

        self.shape      = int(2 * radius + 1), int(2 * radius + 1)
        self.scale      = scale

        self.pix_x      = int( self.shape[0] / 2 )
        self.pix_y      = int( self.shape[1] / 2 )

        self.data       = np.zeros( self.shape )
        self.grid       = np.meshgrid(
            np.arange( self.shape[0] ), np.arange( self.shape[1] )
        )
        self.radial     = np.sqrt(
            (self.grid[0] - self.pix_x)**2 + (self.grid[1] - self.pix_y)**2
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
        ## Determine stamp dimensions based on given information.

        self.WCS        = WCS( header )

        ##  Retrieve alternate coordinates (alpha, delta) <--> (x, y).

        if alpha is not None and delta is not None:

            position    = np.array([[ alpha, delta ]])
            im_x        = self.WCS.wcs_world2pix( position, 1 )[0][1]
            im_y        = self.WCS.wcs_world2pix( position, 1 )[0][0]
            im_x0       = int( im_x )
            im_y0       = int( im_y )
            self.alpha  = alpha
            self.delta  = delta
            self.dx     = im_x - ( im_x0 + .5 )
            self.dy     = im_y - ( im_y0 + .5 )

        elif x is not None and y is not None:

            position    = np.array([[ x, y ]])
            im_x        = x
            im_y        = y
            im_x0       = int( im_x )
            im_y0       = int( im_y )
            self.alpha  = self.WCS.wcs_pix2world( position, 1 )[0][0]
            self.delta  = self.WCS.wcs_pix2world( position, 1 )[0][1]
            self.dx     = im_x - ( im_x0 + .5 )
            self.dy     = im_y - ( im_y0 + .5 )

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

        im_grid         = np.copy( self.grid )
        im_grid[0]     += im_x0 - self.pix_x
        im_grid[1]     += im_y0 - self.pix_y

        try:
            self.data[self.grid]    = image[ im_grid[0], im_grid[1] ]
            self.data               = np.rot90( self.data, k=k )
            self.data              -= np.min( self.data )

        except:
            self.data[self.grid]    = 0.0

    ##  ====================================================================  ##
    ##  Aperture Manipulation

    def set_apertures( self, step=1 ):

        ##  Create array of apertures with the radial space r.
        ##  The extra "1e-8" term is just a temporary bug fix.

        step        = to_pixels( step, self.scale, self.units )
        self.r      = np.arange( 0, self.pix_x, step )
        self.area   = np.pi * self.r**2

        self.aperture   = []
        self.pix_area   = []

        for R in self.r:

            aperture    = np.zeros( self.shape, dtype="int32" ) + 1
            annulus     = np.zeros( self.shape, dtype="int32" ) + 1

            aperture[
                np.where(
                    self.radial > R + 1e-8
                )
            ]   = 0

            self.aperture.append( aperture )
            self.pix_area.append( np.sum(aperture) )

        self.aperture   = np.array( self.aperture )
        self.pix_area   = np.array( self.pix_area )

    def set_annulus( self, Ri, Ro ):

        self.Ri         = to_pixels( Ri, self.scale, self.units )
        self.Ro         = to_pixels( Ro, self.scale, self.units )

        self.annulus    = np.zeros( self.shape, dtype="int32" ) + 1

        self.annulus[
            np.where(
                (self.radial < self.Ri) | (self.radial > self.Ro)
            )
        ]   = 0

    def find_R( self, R ):

        ##  Find and return the ith position of r in which r[i] < R < r[i+1].

        j   = 0

        for i in range( self.r.size - 1 ):

            if self.r[i] <= R and R <= self.r[i+1]:

                j   = i

        return  j

    ##  ====================================================================  ##
    ##  Photometry

    def calc_psf( self, std ):

        std         = to_pixels( std, self.scale, self.units )
        self.psf    = np.exp( -.5 * (self.radial / std)**2 )
        self.frac   = 0 * self.r

        for i in range( self.r.size ):

            self.frac[i]    = np.sum( self.aperture[i] * self.psf )

        self.frac  /= np.sum( self.psf )
        #self.frac  *= self.area / self.pix_area

    def calc_sky( self, sigma=3, epsilon=.03, iters=20 ):

        ##  Iteratively remove outliers and calculate statistics.

        sky_data    = self.data[ np.where( self.annulus > 0 ) ]

        while True:

            iters      -= 1

            mean0       = np.mean( sky_data )
            std         = np.std( sky_data )
            sky_data    = sky_data[
                np.where( sky_data < mean0 + sigma * std )
            ]

            self.sky        = 2.5*np.median(sky_data) - 1.5*np.mean(sky_data)
            self.sky_std    = std

            if np.abs( mean0 - self.sky ) / mean0 < epsilon or iters <= 0:
                break

    def calc_flux( self, subtract=False, psf=False ):

        self.flux       = 0 * self.r
        self.profile    = 0 * self.r
        self.slope      = 0 * self.r
        self.curvature  = 0 * self.r

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

        ##  Initialize smoothed profile.

        self.profile[:] = self.flux[:]

    def calc_profile( self, std ):

        std             = to_pixels( std, self.scale, self.units )

        for i in range( 1, self.r.size - 1 ):

            weights = np.exp( -.5 * ((self.r - self.r[i]) / std)**2 )
            self.profile[i] = np.average( self.flux, weights=weights )

        ##  Calculate the slope ( d(flux)/dr ) of the flux.

        self.slope[1:-1]    = (self.profile[1:-1] - self.profile[:-2])
        self.slope[1:-1]   /= (self.r[1:-1] - self.r[0:-2])

        #self.slope[0]       = self.slope[1]
        #self.slope[-1]      = 0

        min_slope           = np.min( self.slope[2:-2] )
        self.slope         -= min_slope

        ##  Calculate the derivative of the slope.

        self.curvature[1:-1]    = (self.slope[1:-1] - self.slope[:-2])
        self.curvature[1:-1]   /= (self.r[1:-1] - self.r[0:-2])

        ##  Subtract the sky.

        self.sky            = min_slope * self.r
        self.flux          -= self.sky
        self.profile       -= self.sky

    def get_flux( self, R ):

        R   = to_pixels( R, self.scale, self.units )

        ##  Estimate the flux at the specifed radius by linear interpolation.

        i       = self.find_R( R )
        dR      = R - self.r[i]

        return  self.profile[i] + (dR * self.slope[i+1])

    def get_psf_flux( self, subtract=False ):

        if subtract is True:
            return  np.sum( self.psf * (self.data - self.sky) )
        else:
            return  np.sum( self.psf * self.data )

    ##  ====================================================================  ##
    ##  Plotting

    def plot_stamp( self,
        axes, R=None, annulus=True,
        sigma=3, epsilon=0.03, cmap="gray", color="y"
    ):

        axes.imshow(
            Photopy.rescale( self.data, sigma=sigma, epsilon=epsilon ),
            cmap=cmap
        )

        ##  Draw apertures.

        if R is not None:

            if isinstance( R, (int, float) ):
                R   = [ R ]

            for r in R:

                r   = to_pixels( r, self.scale, self.units )

                axes.add_artist(
                    pyplot.Circle(
                        (self.pix_x, self.pix_y), radius=r,
                        color=color, lw=2, fill=False
                    )
                )

        ##  Draw annulus.

        if annulus is True and self.annulus is not None:

            axes.add_artist(
                pyplot.Circle(
                    (self.pix_x, self.pix_y), radius=self.Ri,
                    color=color, linestyle="--", lw=2, fill=False
                )
            )

            axes.add_artist(
                pyplot.Circle(
                    (self.pix_x, self.pix_y), radius=self.Ro,
                    color=color, linestyle="--", lw=2, fill=False
                )
            )

    def plot_profile( self,
        axes, R=None, annulus=True, yscale="log"
    ):

        axes.set_ylim( 0, 1.1 )

        flux        = self.flux / np.max(self.flux)
        profile     = self.profile / np.max(self.flux)
        slope       = self.slope / np.max(self.slope)
        curvature   = self.curvature / np.max(self.slope)
        area        = self.area / self.pix_area

        ##  Plot the basic flux profile.

        axes.plot( self.r, profile,     "b" )
        axes.plot( self.r, flux,        "ko", ms=2 )
        axes.plot( self.r, slope,       "c-" )
        axes.plot( self.r, curvature,   "c--" )
        axes.plot( self.r, area,        "r--" )

        ##  Plot aperture lines.

        if R is not None:

            if isinstance( R, (int,float) ):
                R   = [ R ]

            for r in R:

                flux    = self.get_flux( r ) / np.max(self.flux)
                r       = to_pixels( r, self.scale, self.units )
                axes.plot( [r, r], [0, flux], "y" )

        ##  Plot the annulus.

        if annulus is True:

            Ri      = self.Ri * self.scale
            Ro      = self.Ro * self.scale

            flux    = self.get_flux( Ri ) / np.max(self.flux)
            axes.plot( [self.Ri, self.Ri], [0, flux], "y--" )

            flux    = self.get_flux( Ro ) / np.max(self.flux)
            axes.plot( [self.Ro, self.Ro], [0, flux], "y--" )

        ##  Set the scaling.

        try:
            axes.set_yscale( yscale )
        except:
            pass

    def create_figure( self,
        R=None, sigma=3, epsilon=0.03, yscale="log", saveas=False
    ):

        Fig     = pyplot.figure( figsize=(14,6) )
        Ax1     = Fig.add_subplot( 1,2,1 )
        Ax2     = Fig.add_subplot( 1,2,2 )

        Ax1.set_xlabel("x [pixel]")
        Ax1.set_ylabel("y [pixel]")

        Ax2.set_xlabel("Aperture [pixel]")
        Ax2.set_ylabel("Flux [normalized]")

        self.plot_stamp( Ax1, R=R, sigma=sigma, epsilon=epsilon )
        self.plot_profile( Ax2, R=R, yscale=yscale )

        if saveas is False:
            pyplot.show()
        else:
            try:    ##  This is because of more problems with the log scale.
                pyplot.savefig( saveas )
            except:
                pass
