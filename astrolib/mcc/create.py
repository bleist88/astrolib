"""
MCC/create.py

This contains the function MCC.create() which creates a new FITS Cube from
the configurations files.
"""

from   .__imports__ import *

##  ============================================================================

def create( mcc_file, configs_file, path="." ):

    Timer   = Io.Timer("MCC  -  Master Catalog Correlation")

    Timer.start("MCC")

    ##  Read in the configuration files.
    ##  Set file path variables.

    configs = Io.read( configs_file )

    ##  Initialize the master catalog object.

    if os.path.isfile( mcc_file ):
        FM  = MCC.Field_Manager( mcc_file )

    else:
        FM  = MCC.Field_Manager( mcc_file, init=True )

    ## Loop through all catalog configurations and add them to the Cube.

    for i in range( len(configs) ):

        ##  Retrieve configurations.
        ##  Retrieve image configurations specific to the input catalog.
        ##  Read in the input catalog.

        name        = configs[i]["name"]
        cat_file    = os.path.join( path, configs[i]["catalog"] )
        Rc          = configs[i]["Rc"] / 3600
        append      = configs[i]["append"]

        if append.lower() == "true":
            append  = True
        else:
            append  = False

        ##  This is  currently not needed now that image_managers are use.
        ##
        # images      = []
        # for j in range( len(configs) ):
        #     if configs[j]["name"] == configs[i]["name"]:
        #         images.append( configs[j]["image"] )

        ##   Make sure the catalog is not already added.

        if name in FM.list:
            continue

        ##  Correlate and add catalog to the Master Catalog.

        Timer.start(
            "correlation",
            alert="\nAdding %s to the Master Catalog..." % name
        )

        catalog = Io.read( cat_file )
        FM.add_catalog( name, catalog, Rc, append=append )

        Timer.end("correlation")

    print(
        "\nThe Master Catalog '%s' has been successfully created." % mcc_file
    )

    Timer.end("MCC")
