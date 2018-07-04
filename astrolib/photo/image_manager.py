"""
This file houses the image manager.
"""

from .__imports__   import *

##  ============================================================================

class image:

    def __init__( self, file_name, init=False ):

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

        if init is False:
            self.open( file_name )

    def save( self, saveas=None, overwrite=False ):
        """
        Saves the object to a python pickle file.

        Arguments:
            saveas=None     - file path to save to; if None, uses existing path
            overwrite=False - if overwrite=True, overwrites existing file paths
        """

        ##  Write all members to a dictionary.

        members = {}

        for key in self.__dict__:
            members[ key ]  = self.__dict__[ key ]

        members["wcs"]  = None      ##  this can't be serialized :(

        ##  Serialize to a file.

        if saveas in os.listdir():
            if overwrite is True:
                pyarrow.serialize_to( members, saveas )
            else:
                raise   Exception("%s already exists." % saveas )
        else:
            pyarrow.serialize_to( members, saveas )

    def open( self, file_name ):

        members = pyarrow.read_serialized( file_name ).deserialize()

        for key in members:
            self.__dict__[ key ]    = members[ key ]

##  ============================================================================

class image_manager:

    def __init__( self, file_name, t=None, i=None, f=None, a=None, init=False ):

        self.file_name  = file_name
        self.filter     = f
        self.telescope  = t
        self.instrument = i
        self.author     = a

        self.tiled      = False         ##  are there more than 1 tiles?
        self.files      = {             ##  paths to files
            "sci":  None,
            "bkg":  None,
            "wht":  None,
            "var":  None,
            "unc":  None,
            "flg":  None,
            "cov":  None,
            "chk":  None,
        }
        self.headers    = {
            "sci":  None,
            "bkg":  None,
            "wht":  None,
            "var":  None,
            "unc":  None,
            "flg":  None,
            "cov":  None,
            "chk":  None,
        }

        self.pix_scale  = 1.0           ##  pixel scale
        self.seeing     = 1.0           ##  seeing resolution
        self.gain       = 1.0           ##  gain in (e-/adu)
        self.mag_zero   = 30.0          ##  magnitude zeropoint (AB)
        self.dmag_zero  = 0.0           ##  magnitude zeropoint error

        self.WCS        = None          ##  astropy.wcs.WCS
        self.shape      = None          ##  array shape
        self.x_c        = None          ##  center pixel x
        self.y_c        = None          ##  center pixel y
        self.alpha_c    = None          ##  center pixel ra
        self.delta_c    = None          ##  center pixel dec
        self.theta      = None          ##  orientation in radians

        self.date       = None          ##  date / time
        self.time       = None
        self.julian     = None

        self.comments   = []           ##  comments / history
        self.history    = []

        if init is False:
            self.open( file_name )

    ##  ========================================================================

    def save( self, saveas=None, overwrite=False ):
        """
        Saves the object to a python pickle file.

        Arguments:
            saveas=None     - file path to save to; if None, uses existing path
            overwrite=False - if overwrite=True, overwrites existing file paths
        """

        if saveas is None:
            saveas  = self.file_name

        io.save_obj( self, saveas, overwrite=overwrite )

    def open( self, file_name, force=False ):
        """
        Opens and retrieves the class attributes from an existing pickle file.

        Arguments:
            file_name       - file path to open
        """

        io.open_obj( self, file_name, force=force )

    ##  ========================================================================

    # def write_sex( out_name, default=None, weight=False, flag=False ):
    #
    #     ##  Read in the default configs file.  If there is no default .sex file
    #     ##  then drop one using "sex -dd".
    #
    #     if default is None:
    #         print("Currently this action only supports having a default .sex.")
    #
    #     else:
    #         sex_configs     = io.get_configs( default )
    #
    #     ##  Handle output file names.
    #
    #     sex_configs["CATALOG_NAME"]     = sex_file.replace( ".sex", ".cat" )
    #     sex_configs["CHECKIMAGE_NAME"]  = sex_file.replace( ".sex", ".chk.fits" )
    #
    #     ##  Handle basic parameters.
    #
    #     sex_configs["PIXEL_SCALE"]      = self.pixel_scale
    #     sex_configs["SEEING"]           = self.seeing
    #
    #     ##  Handle weight and flag image options.
    #
    #     if weight is False or weight is None:
    #
    #         sex_configs.pop( "WEIGHT_IMAGE" )
    #         sex_configs.pop( "WEIGHT_TYPE" )
    #         sex_configs.pop( "WEIGHT_GAIN" )
    #
    #     else:
    #
    #         if weight in ["wht", "weight"]:
    #             sex_configs["WEIGHT_IMAGE"]     = self.wht_image
    #             sex_configs["WEIGHT_TYPE"]      = "MAP_WEIGHT"
    #
    #         elif weight in ["var", "variance"]:
    #             sex_configs["WEIGHT_IMAGE"]     = self.var_image
    #             sex_configs["WEIGHT_TYPE"]      = "MAP_VAR"
    #
    #         elif weight in ["bgr", "background"]:
    #             sex_configs["WEIGHT_IMAGE"]     = self.bgr_image
    #             sex_configs["WEIGHT_TYPE"]      = "BACKGROUND"
    #
    #         else:
    #             raise   Exception( "Weight type %s is not understood." % weight )
    #
    #     if flag is False or flag is None:
    #         sex_configs.pop( "FLAG_IMAGE" )
    #         sex_configs.pop( "FLAG_TYPE" )
    #
    #     else:
    #         sex_configs["FLAG_IMAGE"]   = flag
    #
    #     ##  Write the new configurations as a .sex file.
    #
    #     print( "Writing SExtractor configurations into %s..." % sex_file )
    #
    #     io.write_configs( sex_file, sex_configs )
