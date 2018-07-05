"""
This module houses functions used in assisting SExtractor.
"""

from .__imports__ import *

##  ============================================================================

var_changes     = { ##  keyname change replacements
    "PIXEL_SCALE":      "scale",
    "SEEING_FWHM":      "seeing",
    "GAIN":             "gain",
    "MAG_ZEROPOINT":    "zero",
}

##  ============================================================================

def sex( fits_file, sex_file, detection=None, command='sex' ):
    """
    This function performs a SExtractor run on the .fits file using parameters
    from the .sex file.
    """

    ##  Pass the system command to run SExtractor.
    ##  The command:    sex (source_file,)fits_file -c configs_file
    ##  Note!  SExtractor does not work if there is a space after the comma.

    if detection is not None:

        fits_file   = ",".join( [detection, fits_file] )

    command    += " " + fits_file

    if sex_file is not None:

        command    += ' -c ' + sex_file

    print( command )
    os.system( command )

##  ============================================================================

def write_sex( image_manager, bsex_file, sex_file ):
    """
    This function reads in a .bsex file to write a .sex file for an image with
    details provided by the image manager.
    """

    ##  Read in both .bsex and .sex files.

    bsex_configs     = io.get_configs( bsex_file )

    ##  Handle file names.

    telescope   = spec["telescope"][0]
    Filter      = Instrument + "_" + Filter

    sex_file    = "Astromatic/Configs/" + Filter + ".sex"
    cat_file    = "Astromatic/Catalogs/" + Filter + ".cat"

    flag_file   = "Data/" + telescope + "/" + Filter + ".flg.fits"
    check_file  = "Data/" + telescope + "/" + Filter + ".chk.fits"
    weight_file = "Data/" + telescope + "/" + Filter + ".wht.fits"
    var_file    = "Data/" + telescope + "/" + Filter + ".var.fits"
    bg_file     = "Data/" + telescope + "/" + Filter + ".bg.fits"

    ##  Test for flag images.

    if os.path.isfile( flag_file ):
        sex_configs["FLAG_IMAGE"]   = flag_file

    else:
        sex_configs.pop( "FLAG_IMAGE" )
        sex_configs.pop( "FLAG_TYPE" )

    ##  Test for weighs, variance or background images.

    if os.path.isfile( weight_file ):
        sex_configs["WEIGHT_IMAGE"] = weight_file
        sex_configs["WEIGHT_TYPE"]  = "MAP_WEIGHT"

    elif os.path.isfile( var_file ):
        sex_configs["WEIGHT_IMAGE"] = var_file
        sex_configs["WEIGHT_TYPE"]  = "MAP_VAR"

    elif os.path.isfile( bg_file ):
        sex_configs["WEIGHT_IMAGE"] = bg_file
        sex_configs["WEIGHT_TYPE"]  = "BACKGROUND"

    else:
        sex_configs.pop( "WEIGHT_IMAGE" )
        sex_configs.pop( "WEIGHT_TYPE" )
        sex_configs.pop( "WEIGHT_GAIN" )

    ##  Replace the appropriate .sex file default values from .specs file.

    for config in sex_configs:
        if config in var_changes:
            sex_configs[config] = spec[ var_changes[config] ][0]

    ##  Replace file names for catalog, flag, and check images.

    sex_configs["CATALOG_NAME"]     = cat_file
    sex_configs["CHECKIMAGE_NAME"]  = check_file
    sex_configs["FLAG_IMAGE"]       = flag_file

    ##  Write the new configurations as a .sex file.

    print( "Writing %s..." % sex_file )

    io.write_configs( sex_file, sex_configs )

##  ============================================================================

def write_batch( sex_file, bsex_file, detection=None, command="sex" ):
    """
    This function writes a batch of .sex files given a .bsex file and the .sex
    template.
    """

    print( "Writing a .sex file for each image in the batch %s..." % bsex_file )

    bsex_configs    = Io.read( bsex_file )

    for bsex_config in bsex_configs:

        print( "..." + bsex_config["fits_image"] + "." )

        write_sex( sex_file, bsex_config )

##  ============================================================================

def batch_sex( sex_file, bsex_file, detection=None, command="sex" ):
    """
    This performs a "batch" SExtractor run on multiple images listed in the
    'batch_cfg' file which overwrites the default configs in 'default_cfg'.
    """

    ##  Write a .sex file for each in the batch.

    print( "Performing a batch SExtractor run on %s." % bsex_file )

    bsex_configs    = Io.read( bsex_file )

    for bsex_config in bsex_configs:

        sex_file    = None  ##  I need to get this from what was written by
                            ##  write_sex().

        sex( bsex_config["fits_image"], sex_file, detection=detection, command=command )

##  ============================================================================

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
