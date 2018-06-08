"""
This module houses functions used in assisting SExtractor.
"""

from .__imports__ import *

##  ========================================================================  ##

var_changes     = {

    "PIXEL_SCALE":      "scale",       ##  keyname change replacements
    "SEEING_FWHM":      "seeing",
    "GAIN":             "gain",
    "MAG_ZEROPOINT":    "zero",
}

##  ========================================================================  ##

def sex( fits_file, sex_file, detection=None, command='sex' ):
    """
    Run SExtractor on a single image using a sextractor '.sex' file.

    Parameters:
        fits_file:      FITS Image name.
        configs_file:   The .sex file with SExtractor configurations.
        detection:      FITS Image used in for detection in dual image mode.
        command:        The terminal command.
    """

    ##  Pass the system command to run SExtractor.
    ##  The command:    sex (source_file,)fits_file -c configs_file
    ##  Note!  Be sure to have no space after comma for detection image

    if detection is not None:

        fits_file   = ",".join( [detection, fits_file] )

    command    += " " + fits_file

    if sex_file is not None:

        command    += ' -c ' + sex_file

    print( command )
    os.system( command )

##  ========================================================================  ##

def write_sex( Instrument, Filter, specs_file, sex_file ):

    ##  Read in both .specs file and .sex files.
    ##  Find the appropriate spec.

    specs       = Io.read( specs_file )
    sex_configs = Io.get_configs( sex_file )

    a           = np.where(
        (specs["instrument"]    == Instrument) &
        (specs["filter"]        == Filter)
    )[0]

    spec    = specs[a]

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

    Io.write_configs( sex_file, sex_configs )

##  ========================================================================  ##

def batch_sex( Instrument, bsex_file, sex_file, detection=None, command="sex" ):
    """
    This performs a "batch" SExtractor run on multiple images listed in the
    'batch_cfg' file which overwrites the default configs in 'default_cfg'.
    """

    print()
    print( "Starting a batch SExtractor run for %s..." % Instrument )
    print()

    ##  Read in the specs file.
    ##  Select all from batch.

    specs   = Io.read( specs_file )
    a       = np.where( specs["instrument"] == Instrument )[0]
    specs   = specs[a]

    ##  Write a .sex file for each.
    ##  Perform SExtractor runs on each.

    for spec in specs:

        Telescope   = spec["telescope"]
        Filter      = spec["filter"]

        image_file  = "Data/" + Telescope + "/" + Instrument + "_" + Filter + ".fits"
        im_sex_file = "Astromatic/Configs/" + Instrument + "_" + Filter + ".sex"

        write_sex( Instrument, Filter, specs_file, sex_file )

        print( "SExtracting %s with %s..." % (image_file, im_sex_file) )
        print()

        sex( image_file, im_sex_file, detection=detection, command=command )
