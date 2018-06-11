
from .__imports__ import *

##  ========================================================================  ##

class PIM:

    def __init__( self, file_name, init=False, clobber=False ):

        ##  Members

        self.file_name      = file_name
        self.header         = None

        self.sci            = None
        self.sky            = None
        self.var            = None
        self.mask           = None
        self.grid           = None

        self.wcs            = None      ##  world coordinate system (astropy)
        self.theta          = None      ##  rotation angle to north
        self.x0             = None
        self.y0             = None
        self.a0             = None
        self.b0             = None

        self.scale          = None
        self.seeing         = None
        self.psf            = None

        self.exposure       = None
        self.gain           = None
        self.zero           = None
        self.dzero          = None
        self.limit          = None
        self.dlimit         = None

        ##  Initialize from fits file.

        if init is True:

            self.file_name  = file_name.replace( ".fits", ".pim" )
            self.sci        = fits.getdata( file_name )
            self.header     = fits.getheader( file_name )
            self.wcs        = WCS( self.header )

        elif init is False and ".fits" not in file_name:

            self.open( file_name )

    ##  ====================================================================  ##
    ##  File Management

    def save( self, saveas=None, clobber=False ):

        ##  Keep same filename if none is provided.

        if saveas is None:
            saveas  = self.file_name

        ##  Save file.

        if os.path.isfile( saveas ) and clobber is False:
            raise   Exception( saveas + " already exists." )

        else:
            self.grid   = None
            pickle.dump( self, gzip.open(self.file_name, "wb") )

    def open( self, file_name, init=False ):

        pim  = pickle.load( gzip.open(file_name, "rb") )

        self.file_name      = file_name
        self.header         = pim.header

        self.sci            = pim.sci
        self.sky            = pim.sky
        self.var            = pim.var
        self.mask           = pim.mask
        self.grid           = pim.grid

        self.wcs            = pim.wcs
        self.theta          = pim.theta
        self.x0             = pim.x0
        self.y0             = pim.y0
        self.a0             = pim.a0
        self.b0             = pim.b0

        self.scale          = pim.scale
        self.seeing         = pim.seeing
        self.psf            = pim.psf

        self.exposure       = pim.exposure
        self.gain           = pim.gain
        self.zero           = pim.zero
        self.dzero          = pim.dzero
        self.limit          = pim.limit
        self.dlimit         = pim.dlimit

        del pim

    ##  ====================================================================  ##
    ##  Coordinate Handling

    def grid_on( self ):

        self.grid   = np.meshgrid(
            np.arange( self.data.shape[0] ),
            np.arange( self.data.shape[1] )
        )

    ##  ====================================================================  ##
    ##  Display

    def info( self ):

        print( "file_name       ", self.file_name )
        print( "theta           ", self.theta )
        print( "x0              ", self.x0 )
        print( "y0              ", self.y0 )
        print( "a0              ", self.a0 )
        print( "b0              ", self.b0 )
        print( "scale           ", self.scale )
        print( "seeing          ", self.seeing )
        print( "exposure        ", self.exposure )
        print( "gain            ", self.gain )
        print( "zero            ", self.zero )
        print( "dzero           ", self.dzero )
        print( "limit           ", self.limit )
        print( "dlimit          ", self.dlimit )

    def display( self, sigma=3.0, epsilon=0.03, iters=20, cmap="gray" ):

        data    = Maths.clean_sample(
            self.data, sigma=sigma, epsilon=epsilon, iters=iters
        )

        pyplot.imshow( data, cmap=cmap )
        pyplot.show()
