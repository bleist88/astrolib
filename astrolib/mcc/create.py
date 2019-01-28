"""
This contains the function mcc.create() which creates a new FITS Cube from
the configurations files.
"""

from ._imports import *

##  ============================================================================

def create( fits_file, configs_file, path="." ):

    timer   = io.timer("mcc  -  master catalog correlation")
    timer.start("mcc")

    ##  Read in the configuration files.
    ##  Set file path variables.

    configs = io.read( configs_file )

    ##  Initialize the master catalog object.

    if os.path.isfile( fits_file ):
        FM  = mcc.master( fits_file, init=False )

    else:
        FM  = mcc.master( fits_file, init=True )

    ## Loop through all catalog configurations and add them to the Cube.

    for i in range( len(configs) ):

        ##  Retrieve configurations.
        ##  Retrieve image configurations specific to the input catalog.
        ##  Read in the input catalog.

        name        = configs[i]["name"]
        cat_file    = os.path.join( path, configs[i]["catalog"] )
        Rc          = configs[i]["Rc"]
        append      = configs[i]["append"]

        if append.lower() == "true":
            append  = True
        else:
            append  = False

        ##  This is  currently not needed now that image_managers are use.
        ##  Add images to the header.
        # images      = []
        # for j in range( len(configs) ):
        #     if configs[j]["name"] == configs[i]["name"]:
        #         images.append( configs[j]["image"] )

        ##   Make sure the catalog is not already added.

        if name in FM.catalogs:
            continue

        ##  Correlate and add catalog to the Master Catalog.

        timer.start(
            "correlation",
            alert="\nAdding %s to the Master Catalog..." % name
        )

        catalog = io.read( cat_file )
        FM.correlate( name, catalog, Rc, append=append )
        FM.save( FM.fits_file, overwrite=True )

        timer.end("correlation")

    print(
        "\nThe Master Catalog '%s' has been successfully created." % fits_file
    )

    timer.end("mcc")
