"""
This module houses functions used in assisting SExtractor.
"""

from ._imports import *

##  ============================================================================

var_changes     = {     ##  Sextractor Key, Header Key
    "PIXEL_SCALE":      "pix_scale",
    "SEEING_FWHM":      "seeing",
    "GAIN":             "gain",
    "MAG_ZEROPOINT":    "mag_0",
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
    command    += ' -c ' + sex_file

    print( command )
    os.system( command )

##  ============================================================================

def write_sex( fits_file, bsex_file, sex_file, out_dir="." ):
    """
    This function creates a .sex file given the file paths to a FITS image and
    a 'batch' .sex file, which contains general parameters to a batch of images.
    """

    ##  Read in the fits image and batch sex file.

    image   = photo.image( fits_file )
    configs = io.read_configs( bsex_file )

    ##  Handle file names.  Each output file will take the same name as the fits
    ##  image but with different extensions.  The weight images should also
    ##  have the same name as the science image but with _wht.fits as the ext.
    ##  The various files include:
    ##      in  - weight image (_wht.fits), flag image (_flg.fits)
    ##      out - output catalog (.cat), check image (_chk.fits)

    data_dir    = io.parse_path( fits_file )[0]
    name        = io.parse_path( fits_file )[1]

    configs["CATALOG_NAME"] = os.path.join(
        out_dir, name + ".cat"
    )

    configs["CHECKIMAGE_NAME"] = os.path.join(
        out_dir, name + "_chk.fits"
    )

    if configs["FLAG_IMAGE"] is True:
        flag_file   = os.path.join( data_dir, name + "_flg.fits" )
    else:
        configs.pop( "FLAG_IMAGE" )
        configs.pop( "FLAG_TYPE" )

    if configs["WEIGHT_IMAGE"] is True:
        weight_file = os.path.join( data_dir, name + "_wht.fits" )
    else:
        configs.pop("WEIGHT_IMAGE")
        configs.pop("WEIGHT_TYPE")
        configs.pop("WEIGHT_GAIN")

    ##  Use the image meta data in any case 'True' is used.

    if configs["PIXEL_SCALE"] is True:
        configs["PIXEL_SCALE"]      = image.pix_scale
    if configs["SEEING_FWHM"] is True:
        configs["SEEING_FWHM"]      = image.seeing
    if configs["GAIN"] is True:
        configs["GAIN"]             = image.gain * image.exp_time
    if configs["MAG_ZEROPOINT"] is True:
        configs["MAG_ZEROPOINT"]    = image.mag_0

    ##  Write the new configurations as a .sex file.

    print( "Writing %s..." % sex_file )
    io.write_configs( sex_file, configs )

##  ============================================================================

def write_batch( fits_list, bsex_file, out_dir="." ):
    """
    This function writes a batch of .sex files given a .bsex file and the .sex
    template.
    """

    print( "Using the configurations from %s..." % bsex_file )

    ##  Use 'write_sex' for each fits image in the list.
    ##  Create the '.sex' file using the batch sex file path and the image name.

    for fits_file in fits_list:

        configs_dir = io.parse_path( bsex_file )[0]
        image_name  = io.parse_path( fits_file )[1]
        sex_file    = os.path.join( configs_dir, image_name + ".sex" )

        write_sex( fits_file, bsex_file, sex_file, out_dir=out_dir )
