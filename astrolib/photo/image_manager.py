"""
This file houses the image manager.
"""

from .__imports__   import *

##  ============================================================================

class image:

    def __init__( self, file_name ):

        self.file_name  = file_name     ##  file name (.im extension)
        self.filter     = None          ##  filter
        self.telescope  = None          ##  telescope
        self.instrument = None          ##  instrument
        self.author     = None          ##  author

        self.data       = None          ##  image array (tuple if multi==True)
        self.header     = None          ##  header dict (tuple if multi==True)
        self.multi      = False         ##  does it consist of mult. images?
        self.type       = None          ##  image type

        self.pix_scale  = None          ##  pixel scale
        self.seeing     = None          ##  seeing resolution

        self.exp_time   = None          ##  exposure time [s]
        self.gain       = None          ##  gain [e-/adu]
        self.unit       = None          ##  unit of data array
        self.mag_zero   = None          ##  magnitude zeropoint (AB)
        self.dmag_zero  = None          ##  magnitude zeropoint error

        self.wcs        = None          ##  astropy.wcs.WCS object
        self.shape      = None          ##  array shape
        self.x_c        = None          ##  center pixel x
        self.y_c        = None          ##  center pixel y
        self.alpha_c    = None          ##  center pixel ra
        self.delta_c    = None          ##  center pixel dec
        self.theta      = None          ##  orientation in radians

        self.date       = None          ##  date [day-month-year]
        self.time       = None          ##  time [hour:min:sec]
        self.julian     = None          ##  julian time

        self.comments   = []            ##  comments / history
        self.history    = []

        if os.path.isfile( file_name ):
            self.open( file_name )

    def save( self, saveas=None, overwrite=False ):
        """
        Saves the object to a python pickle file.

        Arguments:
            saveas=None     - file path to save to; if None, uses existing path
            overwrite=False - if overwrite=True, overwrites existing file paths

        Note:   Do not serialize a dictionary.  For some reason `pyarrow` does
                not faithfully store large numpy arrays in a dictionary.  Use
                either a list or tuple.
        """

        ##  File options.

        if saveas is None:
            saveas = self.file_name

        if os.path.isfile( saveas ) and overwrite is False:
            raise   Exception( "%s already exists." % saveas )

        ##  Write all members to a dictionary.

        keys    = []
        values  = []

        for key in self.__dict__:

            if key == "wcs":    ##  wcs objects can't be serialized
                continue

            keys.append( key )
            values.append( self.__dict__[key] )

        members = [ keys, values ]

        ##  Serialize to a file.

        pyarrow.serialize_to( members, saveas )

    def open( self, file_name ):

        members = pyarrow.read_serialized( file_name ).deserialize
        keys    = members[0]
        values  = members[1]

        for k, key in enumerate( keys ):

            self.__dict__[ key ]    = values[ k ]

        try:
            self.wcs    = WCS( self.header )
        except:
            self.wcs    = None
