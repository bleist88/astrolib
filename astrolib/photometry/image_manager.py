"""
This file contains the Image_Manager class which manages all image files and
parameters associated with the image.
"""

##  ============================================================================

class Image_Manager:

    def __self__( self, name=None ):

        self.name           = name

        self.telescope      = None      ##  observation
        self.instrument     = None
        self.filter         = None
        self.author         = None

        self.sci_image      = None      ##  image file paths
        self.bgr_image      = None
        self.wht_image      = None
        self.var_image      = None
        self.unc_image      = None
        self.cov_image      = None
        self.flg_image      = None
        self.chk_image      = None

        self.filter         = None      ##  filters
        self.wave_eff       = None
        self.wave_std       = None

        self.pixel_scale    = None      ##  resolution
        self.seeing         = None

        self.mag_type       = None      ##  photometry
        self.mag_zero       = None
        self.dmag_zero      = None
        self.gain           = None
        self.exp_time       = None
        self.flux_unit      = None

        self.date           = None      ##  date / time
        self.time           = None
        self.julian         = None

        self.alpha0         = None      ##  world coordinates
        self.detla0         = None
        self.x0             = None
        self.y0             = None
        self.theta          = None
        self.shape          = None

        self.comments       = []        ##  comments / history
        self.history        = []

    def write_sex( out_name, default=None, weight=False, flag=False ):

        ##  Read in the default configs file.  If there is no default .sex file
        ##  then drop one using "sex -dd".

        if default is None:
            print("Currently this action only supports having a default .sex.")

        else:
            sex_configs     = io.get_configs( default )

        ##  Handle output file names.

        sex_configs["CATALOG_NAME"]     = sex_file.replace( ".sex", ".cat" )
        sex_configs["CHECKIMAGE_NAME"]  = sex_file.replace( ".sex", ".chk.fits" )

        ##  Handle basic parameters.

        sex_configs["PIXEL_SCALE"]      = self.pixel_scale
        sex_configs["SEEING"]           = self.seeing

        ##  Handle weight and flag image options.

        if weight is False or weight is None:

            sex_configs.pop( "WEIGHT_IMAGE" )
            sex_configs.pop( "WEIGHT_TYPE" )
            sex_configs.pop( "WEIGHT_GAIN" )

        else:

            if weight in ["wht", "weight"]:
                sex_configs["WEIGHT_IMAGE"]     = self.wht_image
                sex_configs["WEIGHT_TYPE"]      = "MAP_WEIGHT"

            elif weight in ["var", "variance"]:
                sex_configs["WEIGHT_IMAGE"]     = self.var_image
                sex_configs["WEIGHT_TYPE"]      = "MAP_VAR"

            elif weight in ["bgr", "background"]:
                sex_configs["WEIGHT_IMAGE"]     = self.bgr_image
                sex_configs["WEIGHT_TYPE"]      = "BACKGROUND"

            else:
                raise   Exception( "Weight type %s is not understood." % weight )

        if flag is False or flag is None:
            sex_configs.pop( "FLAG_IMAGE" )
            sex_configs.pop( "FLAG_TYPE" )

        else:
            sex_configs["FLAG_IMAGE"]   = flag

        ##  Write the new configurations as a .sex file.

        print( "Writing SExtractor configurations into %s..." % sex_file )

        io.write_configs( sex_file, sex_configs )
