
from .__imports__ import *

##  ============================================================================

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

##  ============================================================================

class stamp:

    def __init__( self, image, S=10, **params ):

        ##  Data Array Parameters

        self.image      = image     ##  photo.image object

        self.gain       = None      ##  image gain [e-/adu]
        self.exp_time   = None      ##  exposure time [s]
        self.mag_0      = None      ##  image magnitude zeropoint
        self.mag_0_err  = None      ##  image uncertainty in the mag_0
        self.pix_scale  = None      ##  [unit] / pixel

        self.shape      = None      ##  shape of array [pixels]
        self.data       = None      ##  image data array
        self.data_xy    = None      ##  meshgrid (X, Y)
        self.data_r     = None      ##  radial distance array sqrt(X**2 + Y**2)
        self.S          = S         ##  radial width of data array
        self.unit       = None      ##  angle or pixel unit used by user

        self.aperture   = None      ##  aperture array
        self.R          = None      ##  aperture radius
        self.ap_area    = None      ##  true aperture area (number of pixels)
        self.th_area    = None      ##  theoretical aperture area (pi * R**2)

        self.annulus    = None      ##  annulus array
        self.R_i        = None      ##  inner annulus radius
        self.R_o        = None      ##  outer annulus radius
        self.an_area    = None      ##  annulus area (number of pixels)

        self.psf        = None      ##  array of the point spread function
        self.psf_std    = None      ##  standard deviation of the psf
        self.psf_frac   = None      ##  array of psf fraction in aperture

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

        ##  Photometry Parameters

        self.flux       = np.nan    ##  flux through aperture
        self.flux_err   = np.nan    ##  net flux error
        self.mag        = np.nan    ##  magnitude
        self.mag_err    = np.nan    ##  net magnitude error
        self.sky        = np.nan    ##  mean sky estimation
        self.sky_std    = np.nan    ##  deviation in sky value
        self.gain       = np.nan    ##  gain (e-/adu)

        ##  ====================================================================
        ##  Instantiation

        ##  Get parameters from the image object.

        shared_members  = "gain", "exp_time", "mag_0", "mag_0_err", "pix_scale"

        for key in shared_members:
            self.__dict__[ key ]    = image.__dict__[ key ]

        ##  Get kwargs from **params.

        for key in params:
            if key in self.__dict__:
                self.__dict__[ key ]  = params[ key ]

        ##  Deal with units.

        self.S  = to_pixels( S, self.pix_scale, self.unit ) + 0.5

        ##  Create the arrays for the image data, aperture, annulus and psf.

        self.shape      = int( 2 * self.S ), int( 2 * self.S )
        self.x_c        = int( self.shape[0] / 2 )
        self.y_c        = int( self.shape[1] / 2 )

        self.data       = np.zeros( self.shape )
        self.data_xy    = np.meshgrid(
            np.arange( self.shape[0] ), np.arange( self.shape[1] )
        )
        self.data_r     = np.sqrt(
            (self.data_xy[0] - self.x_c)**2 + (self.data_xy[1] - self.y_c)**2
        )

        self.aperture   = np.zeros( self.shape, dtype="float64" )
        self.annulus    = np.zeros( self.shape, dtype="float64" )
        self.psf        = np.zeros( self.shape, dtype="float64" )

    ##  ========================================================================
    ##  Data Manipulation

    def set_target( self, alpha=None, delta=None, x=None, y=None ):

        ##  Retrieve alternate coordinates (alpha, delta) <--> (x, y).
        ##  If alpha and delta are given, calculate x and y.
        ##  If x and y are given, calculate alpha and delta.

        if alpha is not None and delta is not None:

            position    = np.array([[ alpha, delta ]])
            im_x        = self.image.wcs.wcs_world2pix( position, 1 )[0][1]
            im_y        = self.image.wcs.wcs_world2pix( position, 1 )[0][0]
            im_x_c      = int( im_x )
            im_y_c      = int( im_y )

            self.alpha  = alpha
            self.delta  = delta
            self.x_off  = im_x - ( im_x_c + 0.5 )
            self.y_off  = im_y - ( im_y_c + 0.5 )
            self.x      = self.x_c + self.x_off
            self.y      = self.y_c + self.y_off

        elif x is not None and y is not None:

            position    = np.array([[ x, y ]])
            im_x        = x
            im_y        = y
            im_x_c      = int( im_x )
            im_y_c      = int( im_y )

            self.alpha  = self.image.wcs.wcs_pix2world( position, 1 )[0][0]
            self.delta  = self.image.wcs.wcs_pix2world( position, 1 )[0][1]
            self.x_off  = im_x - ( im_x_c + 0.5 )
            self.y_off  = im_y - ( im_y_c + 0.5 )
            self.x      = self.x_c + self.x_off
            self.y      = self.y_c + self.y_off

        else:

            raise   Exception(
                "Both 'alpha' and 'delta' must be supplied or both 'x' and 'y'"\
                "must be supplied."
            )

        ##  Rotate the stamp so that North is up.
        ##  Determine Rotation factor (rotate in k factors of pi/2).
        ##  Get the delta of the pixels around the center.

        around      = np.array([                ##  pixels above, below, to the
            [ im_x_c,       im_y_c + 1  ],      ##  right and to the left.
            [ im_x_c + 1,   im_y_c      ],
            [ im_x_c,       im_y_c - 1  ],
            [ im_x_c - 1,   im_y_c      ]
        ])

        positions   = self.image.wcs.wcs_pix2world( around, 1 )

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
            self.data[ self.data_xy ]   = self.image.data[
                self.data_xy[0] + im_x_c - self.x_c,
                self.data_xy[1] + im_y_c - self.y_c
            ]
            self.data               = np.rot90( self.data, k=k )

        except:
            self.data[ self.data_xy ]   = 0.0

        ##  Determine the radial grid.

        self.data_r     = np.sqrt(
            (self.data_xy[0] - self.x)**2 + (self.data_xy[1] - self.y)**2
        )

    ##  ========================================================================
    ##  Aperture Manipulation

    def set_aperture( self, R ):

        self.R                  = to_pixels( R, self.pix_scale, self.unit )

        r_diff                  = self.R - self.data_r
        inside                  = np.where( r_diff >= 0.5 )
        boarder                 = np.where( (r_diff > -0.5) & (r_diff < 0.5) )

        self.aperture          *= 0.0
        self.aperture[inside]   = 1.0
        self.aperture[boarder]  = r_diff[ boarder ] + 0.5

        self.ap_area            = np.sum( self.aperture )
        self.th_area            = np.pi * self.R**2
        self.frac               = self.ap_area / self.th_area

    def set_annulus( self, R_i, R_o ):

        self.R_i        = to_pixels( R_i, self.pix_scale, self.unit )
        self.R_o        = to_pixels( R_o, self.pix_scale, self.unit )

        self.annulus   *= 0.0
        self.annulus[
            np.where( (self.data_r >= self.R_i) & (self.data_r <= self.R_o) )
        ]   = 1.0

        self.an_area    = np.sum( self.annulus )

    def set_psf( self, std ):

        self.psf_std    = to_pixels( std, self.pix_scale, self.unit )
        self.psf        = np.exp( -.5 * (self.data_r / std)**2 )

        self.psf_frac   = np.sum( self.aperture * self.psf )
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

        ##  Caclulate the flux through the aperture.

        self.flux   = self.frac * np.sum( self.aperture * self.data )

        if subtract is True:
            self.flux  -= self.sky * self.th_area
        if psf is True:
            self.flux  *= self.psf_frac

        self.mag    = self.mag_0 - 2.5 * np.log10( self.flux )

        ##  Error analysis as calculated by calthech:
        ##      Flux-Uncertainty from Aperture Photometry (2008)

        self.flux_err   = np.sqrt(
            (self.flux / self.gain) +
            self.sky_std**2 * (self.th_area + self.th_area**2 / self.an_area)
        )

        self.mag_err    = 1.0857 * self.flux_err / self.flux
        self.mag_err    = np.sqrt( self.mag_err**2 + self.mag_0_err**2 )

    ##  ========================================================================
    ##  Plotting

    def plot_stamp( self, axis, sigma=3, epsilon=0.03, cmap="gray", color="r" ):

        axis.imshow(
            photo.rescale( self.data, sigma=sigma, epsilon=epsilon ),
            cmap=cmap
        )

        ##  Draw apertures.

        axis.plot( self.x, self.y, color + "x", ms=2 )

        if self.R is not None:
            axis.add_artist(
                pyplot.Circle( (self.x, self.y), radius=self.R,
                               color=color, lw=2, fill=False
                )
            )

        if self.Ri_ and self.R_o
            axis.add_artist(
                pyplot.Circle( (self.x, self.y), radius=self.R_i,
                               color=color, linestyle="--", lw=2, fill=False
                )
            )
            axis.add_artist(
                pyplot.Circle( (self.x, self.y), radius=self.R_o,
                               color=color, linestyle="--", lw=2, fill=False
                )
            )

    def plot_aperture( self, axis, annulus=True, cmap="gray", color="r" ):

        if annulus is True:
            axis.imshow( self.aperture + self.annulus, cmap=cmap )
        else:
            axis.imshow( self.aperture, cmap=cmap )

        axis.plot( self.x, self.y, color + "x", ms=2 )

        axis.add_artist(
            pyplot.Circle( (self.x, self.y), radius=self.R,
                           color=color, lw=2, fill=False
            )
        )

        axis.add_artist(
            pyplot.Circle( (self.x, self.y), radius=self.R_i,
                           color=color, linestyle="--", lw=2, fill=False
            )
        )

        axis.add_artist(
            pyplot.Circle( (self.x, self.y), radius=self.R_o,
                           color=color, linestyle="--", lw=2, fill=False
            )
        )

    # def plot_flux( self, axis, R=None, annulus=True, yscale="log" ):
    #
    #     axis.set_ylim( 0, 1.1 )
    #
    #     flux        = self.flux / np.max(self.flux)
    #     slope       = self.profile / np.max(self.profile)
    #     area        = self.area / self.pix_area
    #
    #     ##  Plot the basic flux profile.
    #
    #     axis.plot( self.r,  flux,        "k"    )
    #     axis.plot( self.r,  slope,       "c-"   )
    #     axis.plot( self.r,  area,        "r--"  )
    #
    #     ##  Plot aperture lines.
    #
    #     if R is not None:
    #
    #         if isinstance( R, (int,float) ):
    #             R   = [ to_pixels(R, self.pix_scale, self.unit) ]
    #
    #         else:
    #             for i in range(len(R)):
    #                 R[i] = to_pixels(R, self.pix_scale, self.unit)
    #
    #         for r in R:
    #
    #             flux    = self.get_flux( r ) / np.max( self.flux )
    #             axis.plot( [r, r], [0, flux], "y" )
    #
    #     ##  Plot the annulus.
    #
    #     if annulus is True:
    #
    #         flux    = self.get_flux( self.R_i ) / np.max( self.flux )
    #         axis.plot( [self.R_i, self.R_i], [0, flux], "y--" )
    #
    #         flux    = self.get_flux( self.R_o ) / np.max( self.flux )
    #         axis.plot( [self.R_o, self.R_o], [0, flux], "y--" )
    #
    #     ##  Set the scaling.
    #
    #     try:
    #         axis.set_yscale( yscale )
    #     except:
    #         pass
    #
    # def create_figure( self, R=None, sigma=3, epsilon=0.03, yscale="log", saveas=False ):
    #
    #     Fig     = pyplot.figure( figsize=(14,6) )
    #     Ax1     = Fig.add_subplot( 1,2,1 )
    #     Ax2     = Fig.add_subplot( 1,2,2 )
    #
    #     Ax1.set_xlabel("x [pixel]")
    #     Ax1.set_ylabel("y [pixel]")
    #
    #     Ax2.set_xlabel("Aperture [pixel]")
    #     Ax2.set_ylabel("Flux [normalized]")
    #
    #     self.plot_stamp( Ax1, R=R, sigma=sigma, epsilon=epsilon )
    #     self.plot_flux( Ax2, R=R, yscale=yscale )
    #
    #     if saveas is False:
    #         pyplot.show()
    #     else:
    #         try:    ##  This is because of more problems with the log scale.
    #             pyplot.savefig( saveas )
    #         except:
    #             pass
